#!/usr/bin/env python3
"""The geocode benchmark `dev` split (IOB-labeled, no commas) to the shared record format.

    uv run python -m tools.sets.geocode_dev     # from $GEOCODE_BENCHMARK (default: doorplate's local-data copy)

Source: github.com/zhengcongyin/geocoding-address-parsing-benchmark at COMMIT, file `dev.txt`. No license is stated, so
the file is never shipped; only its SHA-256 is. The `test` split is excluded (doorplate's rules were written while
reading it). Labels go to usaddress's names (as doorplate's `convert.py` does) and through `usaddress.toml`.
"""

from __future__ import annotations

import collections
import os
import sys
from pathlib import Path

from adapters.base import AlignmentError, Mapping
from tools.sets.common import BUILD, SpanError, check_sha, fetched, set_path, sha256, tokens_to_spans, write_jsonl

NAME = "geocode-dev"
COMMIT = "424f94167c21d1ad3f8e70b50a75174f68dfe1f0"
SHA256 = "a3276155202126cf5604c576672c0ac8604eb9ba359350542b8e38a14cd50b79"
PARTS = {"dev": "neutral (drawn from a geocoder's logs; one-line, uppercase, no commas, street addresses only)"}
LABELS = {
    "HOUSENUM": "AddressNumber",
    "PREDIRECTIONAL": "StreetNamePreDirectional",
    "STREET": "StreetName",
    "ROADTYPE": "StreetNamePostType",
    "POSTDIRECTIONAL": "StreetNamePostDirectional",
    "CITY": "PlaceName",
    "STATE": "StateName",
    "POSTAL": "ZipCode",
}


def read_iob(path: Path):
    """Yield token lists `[(token, usaddress label)]`, one per address (`-END-` closes one)."""
    cur: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "-END-":
            if cur:
                yield cur
            cur = []
            continue
        cur.append((parts[0], LABELS[parts[1].split("-", 1)[1]]))


def source_file() -> Path:
    home = Path(
        os.environ.get(
            "GEOCODE_BENCHMARK",
            fetched("geocode-dev", Path.home() / "projects/temp-postal/doorplate/local-data/geocode-benchmark"),
        )
    )
    return home / "dev.txt"


def convert(path: Path) -> tuple[list[dict], collections.Counter]:
    check_sha(path, SHA256)
    mapping = Mapping("usaddress")
    problems = collections.Counter()
    out = []
    for i, tokens in enumerate(read_iob(path)):
        text = " ".join(t for t, _ in tokens)
        try:
            spans = tokens_to_spans(text, tokens, mapping)
        except (AlignmentError, SpanError, KeyError) as e:
            problems[type(e).__name__] += 1
            continue
        out.append({"id": f"dev-{i:06d}", "text": text, "spans": spans, "part": "dev"})
    return out, problems


def main() -> int:
    records, problems = convert(source_file())
    out = set_path(NAME)
    n = write_jsonl(out, records)
    print(f"{NAME}: {n} records -> {out.relative_to(BUILD.parent)}; dropped: {dict(problems) or 'none'}")
    print(f"  sha256: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
