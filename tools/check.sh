#!/usr/bin/env bash
# The local gate: run before finishing any change. Stops at the first failing step.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s\n' "$1"; }

# --- Python (uv + ruff) ---
if [ -f pyproject.toml ]; then
  step "ruff check";  uv run ruff check .
  step "ruff format"; uv run ruff format --check .
  step "pytest";      uv run pytest -q
fi

printf '\n== all checks passed\n'
