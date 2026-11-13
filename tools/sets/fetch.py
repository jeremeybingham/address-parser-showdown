"""Download the external sources of the step 4 sets, each checked against its pinned SHA-256.

    uv run python -m tools.sets.fetch              # every source not already in place
    uv run python -m tools.sets.fetch senzing-us   # one set (usaddress-tests, libpostal-us, senzing-us, geocode-dev)

Files land in `build/sources/<set>/` (git-ignored), and the converters look there when their environment variable
(`$USADDRESS_TESTS`, `$LIBPOSTAL_HOME`, `$SENZING_TEST_DATA`, `$GEOCODE_BENCHMARK`) is not set. Each URL names a pinned
commit, and the hash is the one the converter checks, so a differing file is deleted and the run stops. The sources
are never shipped (`sets/<set>/MANIFEST.md` says why). The doorplate suite has its own `--fetch` in
`doorplate_suite.py`.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

from tools.sets import geocode_dev, libpostal_us, senzing_us, usaddress_tests
from tools.sets.common import BUILD, SourceError, check_sha

SOURCES_DIR = BUILD / "sources"
RAW = "https://raw.githubusercontent.com"
USADDRESS = f"{RAW}/datamade/usaddress/{usaddress_tests.COMMIT}/measure_performance/test_data"
GEOCODE = f"{RAW}/zhengcongyin/geocoding-address-parsing-benchmark/{geocode_dev.COMMIT}"
LIBPOSTAL = f"{RAW}/openvenues/libpostal/{libpostal_us.COMMIT}"
SENZING = f"{RAW}/Senzing/libpostal-data/{senzing_us.COMMIT}/files/tests/v1.2.0/test_data.csv"

# set -> [(path under build/sources/<set>/, URL, SHA-256)]
SOURCES: dict[str, list[tuple[str, str, str]]] = {
    "usaddress-tests": [(f, f"{USADDRESS}/{f}", sha) for f, sha in usaddress_tests.FILES.items()],
    "libpostal-us": [(f"src/{libpostal_us.FILE}", f"{LIBPOSTAL}/{libpostal_us.FILE}", libpostal_us.SHA256)],
    "senzing-us": [("test_data_v1.2.0.csv", SENZING, senzing_us.SHA256)],
    "geocode-dev": [("dev.txt", f"{GEOCODE}/benchmark_dataset/dev.txt", geocode_dev.SHA256)],
}


def fetch_one(dest: Path, url: str, want: str, opener=urllib.request.urlretrieve) -> bool:
    """Download `url` to `dest` unless `dest` already has the pinned hash. True if it downloaded."""
    try:
        check_sha(dest, want)
        return False
    except SourceError:
        pass
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    opener(url, part)
    try:
        check_sha(part, want)
    except SourceError:
        part.unlink(missing_ok=True)
        raise
    part.replace(dest)
    return True


def fetch(names: list[str], root: Path = SOURCES_DIR, opener=urllib.request.urlretrieve) -> None:
    for name in names:
        for rel, url, want in SOURCES[name]:
            got = fetch_one(root / name / rel, url, want, opener)
            print(f"{name}/{rel}: {'downloaded' if got else 'already in place'}, SHA-256 ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sets", nargs="*", choices=[*SOURCES, []], help="default: all")
    args = ap.parse_args()
    try:
        fetch(args.sets or list(SOURCES))
    except SourceError as e:
        print(f"stopped: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"stopped: download failed ({type(e).__name__})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
