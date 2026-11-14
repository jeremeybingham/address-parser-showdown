#!/usr/bin/env python3
"""The golden set's exported gold rounds to the shared record format, with each record's tier as its `part`.

    uv run python -m tools.sets.golden     # sets/golden/gold/round-*.jsonl -> build/sets/golden.jsonl.gz

The tier comes from `tools/golden/tiers.py` (shape class, then the `normal` mapping check); no parser is run. A record
keeps its `alternatives`, its `flag`, `doubtful`, `rough` and `unscored`; the scorer reports a flagged, doubtful or
rough record apart (`tier/flag`, `tier/doubtful`, `tier/rough`), in no score, and leaves unscored regions out on both
sides.
Only exported rounds are read (a round is exported once every card in it is labeled, `tools/label/README.md`).
"""

from __future__ import annotations

import sys

from tools.golden import tiers
from tools.sets.common import BUILD, check_spans, set_path, sha256, write_jsonl

NAME = "golden"
PARTS = {t: "neutral (the hand-labeled golden set; the tier is fixed by shape class)" for t in tiers.TIERS}


def convert(gold: list[dict], prov: dict[str, dict]) -> list[dict]:
    out = []
    for card in gold:
        tier, cls, _ = tiers.tier_of(prov[card["id"]], card)
        rec = {
            "id": card["id"],
            "text": card["text"],
            "spans": check_spans(card["text"], card["spans"]),
            "part": tier,
            "shape_class": cls,
            "alternatives": card.get("alternatives", []),
        }
        for k in ("flag", "doubtful", "rough", "unscored"):
            if card.get(k):
                rec[k] = card[k]
        out.append(rec)
    return out


def main() -> int:
    gold = tiers.load_gold()
    if not gold:
        print("golden: no exported gold rounds yet (sets/golden/gold/)")
        return 1
    records = convert(gold, tiers.load_provenance())
    out = set_path(NAME)
    n = write_jsonl(out, records)
    print(f"{NAME}: {n} records -> {out.relative_to(BUILD.parent)}")
    print(f"  sha256: {sha256(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
