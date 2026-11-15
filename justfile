# Task runner. `just all` will rebuild every figure from pinned versions (step 7); for now it only checks.

default: check

# The local gate: ruff and pytest
check:
    tools/check.sh

# Fetch sets, check checksums, run every adapter, score, measure speed, write runs/<date>/ (needs the pinned libpostal build)
all: check
    uv run python -m tools.run

# Score a committed run again from its prediction files only: just rescore runs/2026-11-15
rescore RUN:
    uv run python -m tools.run --rescore {{RUN}}
