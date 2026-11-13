"""Score prediction files against gold: per record, per part, and the Parser Score."""

from __future__ import annotations

import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from schema import labels as schema_labels
from scorer import spans as sp
from scorer import stats
from tools.sets.common import PREDICTIONS, SETS_OUT, read_jsonl

FORMULA = Path(__file__).with_name("formula.toml")
FLAGS = ("non_address", "ambiguous")


def load_formula(path: Path = FORMULA) -> dict:
    f = tomllib.loads(path.read_text())
    if abs(sum(g["weight"] for g in f["group"]) - 1) > 1e-9:
        raise ValueError("group weights must sum to 1")
    return f


def scored_coarse(formula: dict) -> set[str]:
    known = schema_labels()
    core = {k for k, v in known.items() if v.scope == "core" and not v.parent}
    return core | set(formula["out_of_scope_scored"])


def part_weights(formula: dict) -> dict[tuple[str, str], float]:
    """Weight of each scored (set, part): the group's weight shared equally."""
    out = {}
    for g in formula["group"]:
        for s, p in g["parts"]:
            out[(s, p)] = g["weight"] / len(g["parts"])
    return out


def role_of(formula: dict, set_name: str, part: str) -> str:
    """`scored`, or why the part is reported apart."""
    if (set_name, part) in part_weights(formula):
        return "scored"
    for a in formula.get("apart", []):
        if a["set"] == set_name and a["part"] in ("*", part):
            return a["why"]
    return "not in the formula (reported apart)"


@dataclass
class Counts:
    """Per-record vectors for one (set, part, parser)."""

    ids: list[str] = field(default_factory=list)
    correct: list[int] = field(default_factory=list)  # coarse record accuracy
    tp: list[int] = field(default_factory=list)
    fp: list[int] = field(default_factory=list)
    fn: list[int] = field(default_factory=list)
    errors: int = 0
    field_counts: dict[str, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0, 0]))
    fine_n: int = 0
    fine_correct: int = 0
    fine_skipped: int = 0  # records whose gold has a coarse-only span: not scorable on the fine track
    fine_counts: dict[str, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0, 0]))

    @property
    def n(self) -> int:
        return len(self.correct)


def _best(golds: list[set], pred: set):
    """The reading the prediction fits best: (matches all, tp, gold set)."""
    return max(((g <= pred, len(g & pred), g) for g in golds), key=lambda t: (t[0], t[1]))


def score_record(rec: dict, pred_spans: list, formula: dict, c: Counts) -> None:
    text = rec["text"]
    coarse_scored = scored_coarse(formula)
    readings = sp.readings([tuple(s) for s in rec["spans"]], rec.get("alternatives", []))
    pred = [tuple(s) for s in pred_spans]

    p = sp.coarse_spans(text, pred, coarse_scored)
    golds = [sp.coarse_spans(text, r, coarse_scored) for r in readings]
    ok, tp, g = _best(golds, p)
    c.ids.append(rec["id"])
    c.correct.append(int(ok))
    c.tp.append(tp)
    c.fp.append(len(p - g))
    c.fn.append(len(g - p))
    for _s, _e, lab in g & p:
        c.field_counts[lab][0] += 1
    for _s, _e, lab in p - g:
        c.field_counts[lab][1] += 1
    for _s, _e, lab in g - p:
        c.field_counts[lab][2] += 1

    # fine track
    leaf = sp.leaves()
    if any(lab in coarse_scored and lab not in leaf for r in readings for _, _, lab in r):
        c.fine_skipped += 1  # a gold span labeled only as a coarse field (usaddress's pre-modifier)
        return
    # Every gold leaf counts for every parser: a field a parser cannot split (libpostal's `road`) is a miss here,
    # which is what this track measures. A parser's claims are listed beside the table, not used to excuse it.
    allowed = {lab for lab in leaf if sp.parent_of(lab) in coarse_scored} | {sp.LETTER}
    fp_set = sp.fine_spans(text, pred, allowed)
    fgolds = [sp.fine_spans(text, r, allowed) for r in readings]
    fgolds = [g for g in fgolds if g] or fgolds
    ok, tp, g = _best(fgolds, fp_set)
    if not g:
        return
    c.fine_n += 1
    c.fine_correct += int(ok)
    for _s, _e, lab in g & fp_set:
        c.fine_counts[lab][0] += 1
    for _s, _e, lab in fp_set - g:
        c.fine_counts[lab][1] += 1
    for _s, _e, lab in g - fp_set:
        c.fine_counts[lab][2] += 1


def effective_part(rec: dict) -> str:
    flag = rec.get("flag")
    return f"{rec.get('part', '')}/{flag}" if flag in FLAGS else rec.get("part", "")


def score_set(set_name: str, parser: str, formula: dict, sets_dir: Path = SETS_OUT, pred_dir: Path = PREDICTIONS):
    """`{part: Counts}` for one parser on one converted set; None if the set or the predictions are missing."""
    set_path = sets_dir / f"{set_name}.jsonl.gz"
    pred_path = pred_dir / set_name / f"{parser}.jsonl.gz"
    if not (set_path.is_file() and pred_path.is_file()):
        return None
    out: dict[str, Counts] = defaultdict(Counts)
    preds = read_jsonl(pred_path)
    for rec in read_jsonl(set_path):
        pr = next(preds)
        if pr["id"] != rec["id"]:
            raise ValueError(f"{set_name}/{parser}: prediction ids differ from the set's")
        c = out[effective_part(rec)]
        if pr.get("error"):
            c.errors += 1
        score_record(rec, [] if pr.get("error") else pr["spans"], formula, c)
    return dict(out)


def aggregate(results: dict, formula: dict, parsers: list[str], subset=None, equal=False):
    """Parser Score and F1 score point estimates (and the weights used) from `results[(set, part)][parser]`.

    `subset`: only these (set, part); weights are renormalized to sum to 1. `equal`: every part the same weight.
    """
    w = part_weights(formula)
    keep = [k for k in w if k in results and (subset is None or k in subset)]
    if equal:
        w = {k: 1.0 for k in keep}
    total = sum(w[k] for k in keep)
    out = {}
    for p in parsers:
        acc = f = 0.0
        for k in keep:
            c = results[k][p]
            acc += w[k] / total * (sum(c.correct) / c.n)
            f += w[k] / total * stats.f1(sum(c.tp), sum(c.fp), sum(c.fn))
        out[p] = (100 * acc, 100 * f)
    return out, keep


def bootstrap(results: dict, formula: dict, parsers: list[str]) -> dict:
    """Paired bootstrap intervals for both scores: records are resampled within each part."""
    w = part_weights(formula)
    keep = [k for k in w if k in results]
    total = sum(w[k] for k in keep)
    B = formula["bootstrap_resamples"]
    acc = {p: np.zeros(B) for p in parsers}
    f1 = {p: np.zeros(B) for p in parsers}
    for i, k in enumerate(keep):
        n = results[k][parsers[0]].n
        counts = stats.resample_counts(n, B, formula["bootstrap_seed"] + i)
        for p in parsers:
            c = results[k][p]
            m = counts @ np.array([c.correct, c.tp, c.fp, c.fn], dtype=np.float32).T
            acc[p] += w[k] / total * m[:, 0] / n
            tp, fp, fn = m[:, 1], m[:, 2], m[:, 3]
            f1[p] += w[k] / total * (2 * tp / np.maximum(2 * tp + fp + fn, 1))
    return {
        p: {"score": stats.percentile_interval(100 * acc[p]), "f1": stats.percentile_interval(100 * f1[p])}
        for p in parsers
    }


def sensitivity(results: dict, formula: dict, parsers: list[str]) -> dict[str, dict[str, float]]:
    """Parser Score under equal weights and with each set left out (weights renormalized)."""
    w = part_weights(formula)
    keep = [k for k in w if k in results]
    table = {"formula weights": aggregate(results, formula, parsers)[0]}
    table["equal weights"] = aggregate(results, formula, parsers, equal=True)[0]
    for s in sorted({k[0] for k in keep}):
        rest = {k for k in keep if k[0] != s}
        if rest:
            table[f"without {s}"] = aggregate(results, formula, parsers, subset=rest)[0]
    return {row: {p: v[0] for p, v in vals.items()} for row, vals in table.items()}


def run(parsers: list[str], formula: dict | None = None, sets_dir: Path = SETS_OUT, pred_dir: Path = PREDICTIONS):
    """Score every set found; `results[(set, part)][parser] = Counts`."""
    formula = formula or load_formula()
    names = sorted({a["set"] for a in formula.get("apart", [])} | {s for g in formula["group"] for s, _ in g["parts"]})
    results: dict = defaultdict(dict)
    missing = []
    for name in names:
        for parser in parsers:
            got = score_set(name, parser, formula, sets_dir, pred_dir)
            if got is None:
                missing.append(name)
                break
            for part, c in got.items():
                results[(name, part)][parser] = c
    return dict(results), sorted(set(missing)), formula


__all__ = ["run", "bootstrap", "sensitivity", "aggregate", "load_formula", "score_set"]
