#!/usr/bin/env python3
"""doorplate's benchmark suite v1 (`compare.jsonl.gz`) to the shared record format.

    uv run python -m tools.sets.doorplate_suite            # from the local doorplate checkout ($DOORPLATE_HOME)
    uv run python -m tools.sets.doorplate_suite --fetch    # download the pinned file from GitHub first (2 MB)

The suite's gold is token labels in usaddress's names; they go through `adapters/mappings/usaddress.toml` (a mapping of
names, not of usaddress's output) and neighbouring tokens with one label become one span. Writes
`build/sets/doorplate-suite.jsonl.gz` and prints counts.
"""

from __future__ import annotations

import argparse
import collections
import os
import sys
import urllib.request
from pathlib import Path

from adapters.base import AlignmentError, Mapping
from tools.sets.common import BUILD, SpanError, check_sha, read_jsonl, set_path, sha256, tokens_to_spans, write_jsonl

NAME = "doorplate-suite"
COMMIT = "3fc5ec4fd79c62f345b7421ea9af9857d123cdc2"  # doorplate commit that froze suite v1
FILE = "benchmarks/suite/v1/compare.jsonl.gz"
SHA256 = "2336f0996f2d044d56d69467f6f3ea7d33a4a64a680decb43179651bf006b430"  # from the suite's own MANIFEST.md
URL = f"https://raw.githubusercontent.com/jeremeybingham/doorplate/{COMMIT}/{FILE}"
# Parts and whether they count in an aggregate: `hard` was drawn from where two of the three parsers fail.
PARTS = {"natural": "neutral", "hand": "neutral", "hard": "reported apart (drawn from two parsers' blind spots)"}
KEEP = ("source", "type", "style")


def source_file(fetch: bool) -> Path:
    if fetch:
        path = BUILD / "sources" / NAME / "compare.jsonl.gz"
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, path)
    else:
        home = Path(os.environ.get("DOORPLATE_HOME", Path.home() / "projects" / "temp-postal" / "doorplate"))
        path = home / FILE
    check_sha(path, SHA256)
    return path


def convert(path: Path) -> tuple[list[dict], collections.Counter]:
    mapping = Mapping("usaddress")
    problems = collections.Counter()
    out = []
    for r in read_jsonl(path):
        try:
            spans = tokens_to_spans(r["input"], [tuple(t) for t in r["tokens"]], mapping)
        except (AlignmentError, SpanError, KeyError) as e:
            problems[type(e).__name__] += 1
            continue
        out.append({"id": r["id"], "text": r["input"], "spans": spans, "part": r["stratum"]} | {k: r[k] for k in KEEP})
    return out, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="download the pinned file instead of reading DOORPLATE_HOME")
    args = ap.parse_args(argv)
    records, problems = convert(source_file(args.fetch))
    out = set_path(NAME)
    n = write_jsonl(out, records)
    parts = collections.Counter(r["part"] for r in records)
    print(f"{NAME}: {n} records -> {out.relative_to(BUILD.parent)}")
    print(f"  parts: {dict(sorted(parts.items()))}; dropped: {dict(problems) or 'none'}")
    print(f"  sha256: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
