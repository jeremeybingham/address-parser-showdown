# Task runner. `just all` will rebuild every figure from pinned versions (step 7); for now it only checks.

default: check

# The local gate: ruff and pytest
check:
    tools/check.sh

# Fetch sets, check checksums, run every adapter, score, write runs/<date>/ (not written yet)
all: check
    @echo "just all: not implemented yet (step 7)"
