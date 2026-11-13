#!/usr/bin/env python3
"""usaddress's own labeled test files (`measure_performance/test_data/`) to the shared record format.

    uv run python -m tools.sets.usaddress_tests            # from $USADDRESS_TESTS (default: doorplate's vendored copy)

Each file is a part. The XML is usaddress's training format (one element per token, named by its label); labels go
through `adapters/mappings/usaddress.toml`. Writes `build/sets/usaddress-tests.jsonl.gz`.
"""

from __future__ import annotations

import collections
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from adapters.base import AlignmentError, Mapping
from tools.sets.common import BUILD, SpanError, check_sha, set_path, sha256, tokens_to_spans, write_jsonl

NAME = "usaddress-tests"
COMMIT = "aa7699b53a0843fc443f9e87285b88cbd9eaf50a"  # datamade/usaddress, 2025-08-07
# file -> SHA-256 (doorplate's vendored copies are unchanged copies of upstream's)
FILES = {
    "us50_test_tagged.xml": "e4dbaa8a7e95fd7d099bfe89ef5881c751f4b4a808c739a8bc2493289eb2e957",
    "labeled.xml": "2a5f222a4c52c73d9abacb3be21b501972d1bfb48ebe7d8bbb80671ea5e755e5",
    "synthetic_osm_data.xml": "8d88c7f334e7dd094e38b37ae19e499c91ebaba51f3e77d3ebccd696e5e1e4b2",
    "synthetic_clean_osm_data.xml": "bd1a2c19e48058fbf2f724803703b9137b9e5d3d907db8273f46ebd6796d9143",
    "simple_address_patterns.xml": "15568e2b9226ca83b6d6a393eb79139e310c64af1494fe13bd5857a512367074",
    "multi_word_state_addresses.xml": "4dd5c864938821a9fb006ae1318f8b390d60c2cdf612d05ab012eb5094d3a7a0",
}
PARTS = {p.removesuffix(".xml"): "home set (usaddress's regression tests)" for p in FILES}


def source_dir() -> Path:
    default = Path.home() / "projects/temp-postal/doorplate-v051/tests/external/usaddress"
    return Path(os.environ.get("USADDRESS_TESTS", default))


def read_xml(path: Path):
    for el in ET.parse(path).getroot():
        tokens = [(c.text or "", c.tag) for c in el]
        text = "".join(el.itertext()).strip()
        yield text, [(t, lab) for t, lab in tokens if t.strip()]


def convert(directory: Path) -> tuple[list[dict], collections.Counter]:
    mapping = Mapping("usaddress")
    problems = collections.Counter()
    out = []
    for fname, want in FILES.items():
        check_sha(directory / fname, want)
        part = fname.removesuffix(".xml")
        for i, (text, tokens) in enumerate(read_xml(directory / fname)):
            try:
                spans = tokens_to_spans(text, tokens, mapping)
            except (AlignmentError, SpanError, KeyError) as e:
                problems[f"{part}:{type(e).__name__}"] += 1
                continue
            out.append({"id": f"{part}-{i:05d}", "text": text, "spans": spans, "part": part})
    return out, problems


def main() -> int:
    records, problems = convert(source_dir())
    out = set_path(NAME)
    n = write_jsonl(out, records)
    print(f"{NAME}: {n} records -> {out.relative_to(BUILD.parent)}")
    print(f"  parts: {dict(sorted(collections.Counter(r['part'] for r in records).items()))}")
    print(f"  dropped: {dict(problems) or 'none'}")
    print(f"  sha256: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
