#!/usr/bin/env python3
"""libpostal's `test_us_parses` (53 cases in `test/test_parser.c`) to the shared record format.

    uv run python -m tools.sets.libpostal_us    # from $LIBPOSTAL_HOME/src (default ~/projects/libpostal-senzing)

Read from the pinned clone, not copied. Gold is libpostal's own label per component (lowercased); it goes through
`adapters/mappings/libpostal.toml`. A home set for libpostal. Writes `build/sets/libpostal-us.jsonl.gz`.
"""

from __future__ import annotations

import collections
import os
import re
import sys
from pathlib import Path

from adapters.base import AlignmentError, Mapping
from tools.sets.common import BUILD, SpanError, check_sha, components_to_spans, set_path, sha256, write_jsonl

NAME = "libpostal-us"
FILE = "test/test_parser.c"
SHA256 = "d979b2606ff6928f9ad0026fba2594bd07b06150b4967d6355bdfc9e5b5714f0"  # the Senzing fork's clone; see MANIFEST.md
PARTS = {"us": "home set (libpostal's own regression tests)"}
CASE = re.compile(r'test_parse_result_equals\(\s*"((?:[^"\\]|\\.)*)",\s*options,\s*(\d+),(.*?)\)\);', re.S)
COMP = re.compile(r'\{"(\w+)",\s*"((?:[^"\\]|\\.)*)"\}')


def source_file() -> Path:
    home = Path(os.environ.get("LIBPOSTAL_HOME", Path.home() / "projects/libpostal-senzing"))
    return home / "src" / FILE


def us_cases(path: Path):
    src = path.read_text(encoding="utf-8")
    start = src.index("TEST test_us_parses")
    end = src.index("\n}\n", start)
    body = re.sub(r"^\s*//.*$", "", src[start:end], flags=re.M)  # comments sit between the call and its string
    for m in CASE.finditer(body):
        comps = COMP.findall(m.group(3))
        if len(comps) != int(m.group(2)):
            raise ValueError("component count differs from the declared count")
        yield m.group(1), comps


def convert(path: Path) -> tuple[list[dict], collections.Counter]:
    check_sha(path, SHA256)
    mapping = Mapping("libpostal")
    problems = collections.Counter()
    out = []
    for i, (text, comps) in enumerate(us_cases(path)):
        try:
            spans = components_to_spans(text, comps, mapping)
        except (AlignmentError, SpanError, KeyError) as e:
            problems[type(e).__name__] += 1
            continue
        out.append({"id": f"us-{i:03d}", "text": text, "spans": spans, "part": "us"})
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
