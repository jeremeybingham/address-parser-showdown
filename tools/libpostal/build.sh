#!/usr/bin/env bash
# Build the pinned libpostal (Senzing model) and its Python binding, and check the data against the pinned checksum.
# Usage: tools/libpostal/build.sh [PREFIX]    (default PREFIX: $LIBPOSTAL_HOME, then ~/projects/libpostal-senzing)
# Needs: git, a C toolchain, autoconf, automake, libtool, pkg-config, curl, uv. Downloads about 3 GB of model data.
# `tools/libpostal/build.sh --verify [PREFIX]` only checks the data of an existing build and records the result in
# `DATA_CHECKSUM.sha256` beside it (the adapter reads that file).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tools/libpostal/pins.env
source "$here/pins.env"

verify_only=0
if [ "${1:-}" = "--verify" ]; then verify_only=1; shift; fi
prefix="${1:-${LIBPOSTAL_HOME:-$HOME/projects/libpostal-senzing}}"

# sha256 of the sorted list of per-file sha256 values of the data directory
data_checksum() { (cd "$1" && find . -type f -print0 | xargs -0 sha256sum | awk '{print $1}' | sort | sha256sum | awk '{print $1}'); }

check_data() {
  local got
  got="$(data_checksum "$prefix/data")"
  echo "data checksum: $got"
  if [ "$got" != "$LIBPOSTAL_DATA_CHECKSUM" ]; then
    echo "MISMATCH: pinned $LIBPOSTAL_DATA_CHECKSUM" >&2
    exit 1
  fi
  echo "matches the pin"
  echo "$got" > "$prefix/DATA_CHECKSUM.sha256"
}

if [ "$verify_only" = 1 ]; then check_data; exit 0; fi

mkdir -p "$prefix"
if [ ! -d "$prefix/src/.git" ]; then git clone https://github.com/openvenues/libpostal "$prefix/src"; fi
cd "$prefix/src"
git fetch -q origin
git checkout -q "$LIBPOSTAL_COMMIT"
./bootstrap.sh
./configure --prefix="$prefix/install" --datadir="$prefix/data" MODEL="$LIBPOSTAL_MODEL"
make -j"$(nproc)"
make install

uv venv --python 3.13 "$prefix/venv"
CFLAGS="-I$prefix/install/include" LDFLAGS="-L$prefix/install/lib" \
  uv pip install -p "$prefix/venv/bin/python" "postal==$PYPOSTAL_VERSION"

echo "$LIBPOSTAL_COMMIT" > "$prefix/LIBPOSTAL_COMMIT.txt"
echo "postal  $PYPOSTAL_VERSION" > "$prefix/POSTAL_VERSION.txt"
check_data
