"""Golden-set breakdowns the report needs and the scorer does not print: by stratum, restored rows, nightmare variant,
and real versus invented text (issue #26). Coarse record accuracy with Wilson intervals, scored the scorer's way
(`scorer.score.score_record`); only records the scorer puts in a tier figure count (one door, sure). In no score.

    uv run python -m tools.report.breakdown RUN_DIR          # from the run's committed predictions (no parser is run)
    uv run python -m tools.report.breakdown RUN_DIR --real   # also the private text (runs every parser; local only)

`--real` reads the private gold (`local-data/golden-real/gold/`, the labels on the row's own text) and parses that text
with every adapter: the same cards scored on the text they were labeled on and on the shipped text with invented values.
It prints counts and percentages only; the private text is never printed.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from scorer.score import Counts, effective_part, load_formula, score_record
from scorer.stats import wilson
from tools.golden import tiers
from tools.sets.common import SETS_OUT, read_jsonl
from tools.sets.golden import convert

PARSERS = ("doorplate", "libpostal", "usaddress")
TIERS = ("normal", "hard", "nightmare")
REAL_GOLD = Path(__file__).resolve().parents[2] / "local-data" / "golden-real" / "gold"


RANDOM_PUBLIC = "public, rounds 1 to 6 and 11 (random walk)"


def groups(prov: dict, shape_class: str = "") -> list[str]:
    """The breakdown rows a record belongs to (besides its tier)."""
    out = [f"stratum={prov['stratum']}", f"class={shape_class}"]
    if prov["stratum"] == "public":
        out.append("public restored" if prov.get("restored") else RANDOM_PUBLIC)
    if prov.get("variant"):
        out.append(f"variant={prov['variant']}")
    if prov.get("round") == 10:
        out.append("source=sba-ppp")
    return out


def table(rows: dict[tuple[str, str], dict[str, list[int]]]) -> str:
    lines = ["| Group | Tier | Records | " + " | ".join(PARSERS) + " |", "|---|---|---|" + "---|" * len(PARSERS)]
    for (g, t), by in sorted(rows.items()):
        n = len(next(iter(by.values())))
        cells = []
        for p in PARSERS:
            k = sum(by[p])
            lo, hi = wilson(k, n)
            cells.append(f"{100 * k / n:.1f} ({100 * lo:.1f} to {100 * hi:.1f})")
        lines.append(f"| {g} | {t} | {n:,} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value: the binomial test of b against b + c at one half."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def discordant(rows: dict, key: tuple[str, str]) -> str:
    """Paired counts on one group: records parser A reads right and B wrong, and the reverse (an exact McNemar test)."""
    by = rows[key]
    lines = ["| Pair | A right, B wrong | B right, A wrong | Exact McNemar p |", "|---|---|---|---|"]
    for i, a in enumerate(PARSERS):
        for b in PARSERS[i + 1 :]:
            ab = sum(x and not y for x, y in zip(by[a], by[b], strict=True))
            ba = sum(y and not x for x, y in zip(by[a], by[b], strict=True))
            pval = mcnemar_exact(ab, ba)
            lines.append(f"| A {a}, B {b} | {ab} | {ba} | {pval:.3f} |")
    return "\n".join(lines)


def score_one(rec: dict, spans: list, formula: dict) -> int:
    c = Counts()
    score_record(rec, spans, formula, c)
    return c.correct[0]


def shipped(run: Path, formula: dict, prov: dict) -> tuple[dict, dict]:
    """Rows from the committed predictions; also the per-record result, id -> parser -> correct."""
    records = list(read_jsonl(SETS_OUT / "golden.jsonl.gz"))
    preds = {p: {r["id"]: r for r in read_jsonl(run / "predictions" / "golden" / f"{p}.jsonl.gz")} for p in PARSERS}
    rows: dict = defaultdict(lambda: defaultdict(list))
    per: dict = {}
    for rec in records:
        if effective_part(rec) not in TIERS:
            continue
        per[rec["id"]] = {}
        for p in PARSERS:
            pr = preds[p][rec["id"]]
            ok = score_one(rec, [] if pr.get("error") else pr["spans"], formula)
            per[rec["id"]][p] = ok
            for g in groups(prov[rec["id"]], rec.get("shape_class", "")):
                rows[(g, rec["part"])][p].append(ok)
                rows[(g, "all tiers")][p].append(ok)
    return rows, per


def real(formula: dict, prov: dict, per: dict) -> dict:
    """The cards whose private text differs from the shipped text, scored on both."""
    from adapters.registry import ADAPTERS

    shipped_text = {r["id"]: r["text"] for r in read_jsonl(SETS_OUT / "golden.jsonl.gz")}
    try:
        cards = [json.loads(line) for f in sorted(REAL_GOLD.glob("round-*.jsonl")) for line in f.open() if line.strip()]
    except Exception as e:  # reader errors can quote card text
        sys.exit(f"private gold: {type(e).__name__}")
    cards = [c for c in cards if c["id"] in per and c["text"] != shipped_text.get(c["id"])]
    recs = convert(cards, prov)
    adapters = {p: ADAPTERS[p]() for p in PARSERS}
    rows: dict = defaultdict(lambda: defaultdict(list))
    for rec in recs:
        if effective_part(rec) not in TIERS:
            continue
        for p, ad in adapters.items():
            try:
                spans = [[s.start, s.end, s.label] for s in ad.canonical(rec["text"])]
            except Exception:
                spans = []
            ok = score_one(rec, spans, formula)
            for t in (rec["part"], "all tiers"):
                rows[("real text", t)][p].append(ok)
                rows[("shipped text (invented values)", t)][p].append(per[rec["id"]][p])
    return rows


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    run = Path(argv[0])
    formula = load_formula()
    prov = tiers.load_provenance()
    rows, per = shipped(run, formula, prov)
    print("## Golden set by stratum, restored rows and nightmare variant (coarse record accuracy, 95% Wilson)\n")
    print(table({k: v for k, v in rows.items() if not k[0].startswith("class=")}))
    print("\n## Golden set by shape class (all tiers)\n")
    print(table({k: v for k, v in rows.items() if k[0].startswith("class=") and k[1] == "all tiers"}))
    print(f"\n## Paired differences on the random public stratum ({RANDOM_PUBLIC}, all tiers)\n")
    print(discordant(rows, (RANDOM_PUBLIC, "all tiers")))
    print("\n## Paired differences on the golden set (all tiers, all strata)\n")
    allrows: dict = defaultdict(list)
    for (g, t), by in rows.items():
        if g.startswith("stratum=") and t == "all tiers":
            for p in PARSERS:
                allrows[p] += by[p]
    print(discordant({("all", "all"): allrows}, ("all", "all")))
    if "--real" in argv:
        print("\n## The same cards on the private text and on the shipped text\n")
        print(table(real(formula, prov, per)))


if __name__ == "__main__":
    main(sys.argv[1:])
