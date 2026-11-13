#!/usr/bin/env python3
"""Senzing's `test_data_v1.2.0.csv`, US rows, to the shared record format.

    uv run python -m tools.sets.senzing_us     # from $SENZING_TEST_DATA (default: doorplate's local-data copy)

Gold is libpostal's component labels per row (lowercased), mapped by `adapters/mappings/libpostal.toml`. Provenance is
mixed, so the file is never shipped, only its SHA-256. Rows from `source=libpostal` are libpostal's `test_us_parses`
(set `libpostal-us`) and are left out here, after a check that their texts are exactly that set's. Parts: `osm`
(OpenStreetMap-derived) and `bug` (`Libpostal-bug`, cases reported against libpostal). Writes
`build/sets/senzing-us.jsonl.gz`.
"""

from __future__ import annotations

import collections
import csv
import os
import sys
from pathlib import Path

from adapters.base import AlignmentError, Mapping
from tools.sets import libpostal_us
from tools.sets.common import (
    BUILD,
    SourceError,
    SpanError,
    check_sha,
    components_to_spans,
    set_path,
    sha256,
    write_jsonl,
)

NAME = "senzing-us"
SHA256 = "db58065bf7508b862e9c6ee68774312bfc7e675192e21b8ee6aa9f7aa32ed51a"
PARTS = {"osm": "neutral (OpenStreetMap-derived)", "bug": "reported apart (cases reported as libpostal bugs)"}
PART_OF = {"osm": "osm", "Libpostal-bug": "bug"}
COLUMNS = [
    "house",
    "house_number",
    "road",
    "po_box",
    "unit",
    "level",
    "staircase",
    "suburb",
    "city_district",
    "city",
    "state_district",
    "state",
    "postcode",
    "country",
    "world_region",
    "category",
    "near",
]


def source_file() -> Path:
    home = Path(
        os.environ.get(
            "SENZING_TEST_DATA", Path.home() / "projects/temp-postal/doorplate/local-data/senzing-libpostal-test"
        )
    )
    return home / "test_data_v1.2.0.csv"


def convert(path: Path) -> tuple[list[dict], collections.Counter]:
    check_sha(path, SHA256)
    mapping = Mapping("libpostal")
    problems = collections.Counter()
    out = []
    lp_texts = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["country_code"] != "us":
                continue
            text = row["full_address"]
            if row["source"] == "libpostal":
                lp_texts.add(text)
                continue
            part = PART_OF[row["source"]]
            comps = [(c, row[c]) for c in COLUMNS if row[c].strip()]
            try:
                spans = components_to_spans(text, comps, mapping)
            except (AlignmentError, SpanError, KeyError) as e:
                problems[f"{part}:{type(e).__name__}"] += 1
                continue
            out.append({"id": f"senzing-{row['record_id']}", "text": text, "spans": spans, "part": part})
    ours = {t for t, _ in libpostal_us.us_cases(libpostal_us.source_file())}
    if lp_texts != ours:
        raise SourceError(f"source=libpostal rows differ from test_us_parses ({len(lp_texts)} vs {len(ours)} texts)")
    return out, problems


def main() -> int:
    records, problems = convert(source_file())
    out = set_path(NAME)
    n = write_jsonl(out, records)
    print(f"{NAME}: {n} records -> {out.relative_to(BUILD.parent)}")
    print(
        f"  parts: {dict(sorted(collections.Counter(r['part'] for r in records).items()))}; "
        f"dropped: {dict(problems) or 'none'}"
    )
    print(f"  sha256: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
