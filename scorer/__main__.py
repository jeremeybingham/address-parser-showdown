"""`uv run python -m scorer [--parsers a,b,c] [--out DIR]`: score the converted sets and print the tables (markdown)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapters.base import Mapping
from scorer import score, stats
from scorer import spans as sp

DEFAULT_PARSERS = ["doorplate", "libpostal", "usaddress"]


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def tables(results: dict, missing: list[str], formula: dict, parsers: list[str]) -> str:
    L: list[str] = []
    w = score.part_weights(formula)
    if missing:
        L += [
            f"> **Incomplete:** no converted set or predictions for: {', '.join(missing)}. "
            "Scores use the parts present, weights renormalized; they are not the Parser Score of the formula.",
            "",
        ]
    L += ["## Record accuracy by part (coarse track, 95% Wilson interval)", ""]
    L += ["| Set / part | Role | Records | " + " | ".join(parsers) + " |", "|---|---|---|" + "---|" * len(parsers)]
    for (s, part), by in sorted(results.items()):
        n = by[parsers[0]].n
        cells = []
        for p in parsers:
            k = sum(by[p].correct)
            lo, hi = stats.wilson(k, n)
            cells.append(
                f"{100 * k / n:.1f} ({100 * lo:.1f} to {100 * hi:.1f})"
                + (f", {by[p].errors} errors" if by[p].errors else "")
            )
        L.append(f"| {s} / {part} | {score.role_of(formula, s, part)} | {n:,} | " + " | ".join(cells) + " |")
    L += ["", "## Field F1 by coarse field (micro over each set's scored parts and parts reported apart)", ""]
    fields = sorted({f for by in results.values() for c in by.values() for f in c.field_counts})
    L += ["| Set / part | Field | " + " | ".join(parsers) + " |", "|---|---|" + "---|" * len(parsers)]
    for (s, part), by in sorted(results.items()):
        for f in fields:
            vals = []
            for p in parsers:
                tp, fp, fn = by[p].field_counts.get(f, [0, 0, 0])
                vals.append("-" if tp + fp + fn == 0 else f"{100 * stats.f1(tp, fp, fn):.1f}")
            if any(v != "-" for v in vals):
                L.append(f"| {s} / {part} | {f} | " + " | ".join(vals) + " |")
    L += [
        "",
        "## Fine track (reported apart; every gold leaf label counts for every parser; gold fully fine-labeled)",
        "",
    ]
    L += [
        "| Set / part | Records | " + " | ".join(f"{p} record accuracy" for p in parsers) + " |",
        "|---|---|" + "---|" * len(parsers),
    ]
    for (s, part), by in sorted(results.items()):
        cells = [f"{100 * by[p].fine_correct / by[p].fine_n:.1f}" if by[p].fine_n else "-" for p in parsers]
        L.append(f"| {s} / {part} | {by[parsers[0]].fine_n:,} of {by[parsers[0]].n:,} | " + " | ".join(cells) + " |")
    leaves = sp.leaves()
    for p in parsers:
        can = sorted(Mapping(p).claims & leaves)
        L.append(
            f"- {p} produces these fine labels: {', '.join(can)}. "
            "A field it labels only as a whole counts as a miss here."
        )
    L += ["", "Per fine label F1 is in `results.json` (`fine_f1`).", ""]
    if any(k in results for k in w):
        boot = score.bootstrap(results, formula, parsers)
        agg, used = score.aggregate(results, formula, parsers)
        L += [
            "## Parser Score",
            "",
            f"Parts used: {', '.join(f'{s}/{p}' for s, p in used)}. Bootstrap: "
            f"{formula['bootstrap_resamples']} resamples, seed {formula['bootstrap_seed']}.",
            "",
        ]
        L += ["| Parser | Parser Score (95% interval) | Field F1 score (95% interval) |", "|---|---|---|"]
        for p in parsers:
            (a, f), b = agg[p], boot[p]
            L.append(
                f"| {p} | {a:.1f} ({b['score'][0]:.1f} to {b['score'][1]:.1f}) "
                f"| {f:.1f} ({b['f1'][0]:.1f} to {b['f1'][1]:.1f}) |"
            )
        L += [
            "",
            "## Sensitivity (Parser Score)",
            "",
            "| Weights | " + " | ".join(parsers) + " |",
            "|---|" + "---|" * len(parsers),
        ]
        for row, vals in score.sensitivity(results, formula, parsers).items():
            order = sorted(parsers, key=lambda p: -vals[p])
            L.append(
                f"| {row} | " + " | ".join(f"{vals[p]:.1f}" for p in parsers) + f" | ranking: {' > '.join(order)} |"
            )
    return "\n".join(L) + "\n"


def to_json(results: dict, parsers: list[str]) -> dict:
    out = {}
    for (s, part), by in sorted(results.items()):
        out[f"{s}/{part}"] = {
            p: {
                "records": c.n,
                "correct": sum(c.correct),
                "errors": c.errors,
                "field_counts": dict(c.field_counts),
                "fine": {"records": c.fine_n, "correct": c.fine_correct, "skipped": c.fine_skipped},
                "fine_f1": {k: round(stats.f1(*v), 4) for k, v in sorted(c.fine_counts.items())},
            }
            for p, c in by.items()
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parsers", default=",".join(DEFAULT_PARSERS))
    ap.add_argument("--out", type=Path, help="write results.md and results.json here")
    args = ap.parse_args()
    parsers = args.parsers.split(",")
    results, missing, formula = score.run(parsers)
    md = tables(results, missing, formula, parsers)
    print(md)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "results.md").write_text(md)
        (args.out / "results.json").write_text(json.dumps(to_json(results, parsers), indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
