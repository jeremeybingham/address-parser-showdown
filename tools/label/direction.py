"""Which way adjudication moved the gold: counts per round and per parser, for the report (METHODOLOGY.md).

For each card, the gold before adjudication is its latest blind save (phase `label`) before the first `adjudicate`
save; the gold after is its latest save. Saves of phase `schema` (a rule applied to every card after the first run,
`tools/golden/highway_alt.py`) are left out: they are not adjudication.

Each parser is run on the card text, and its readings the gold does not hold are listed against both golds
(`adjudicate.disagreements`). Neighbouring spans of one label with only spaces between them are joined first, on both
sides, so saving `NEW YORK` as one city span instead of two is not counted as a change toward the parser that reads it
whole (the scorer joins them the same way). A reading listed before and not after is a change *toward* that parser; a
reading listed after and not before is a change *away* from it. Removed cards are left out. Prints counts only (the
card text is private and never printed).

    uv run python -m tools.label.direction [ROUND...]    # all rounds when none is given
"""

import json
import re
import sys

from tools.label import store
from tools.label.adjudicate import disagreements

ROUNDS = list(range(1, 13))
_SPACE = re.compile(r"\s*")


def join_words(text: str, spans) -> list[tuple[int, int, str]]:
    """One span per run of a label: neighbours of one label with only whitespace between them are joined."""
    out: list[list] = []
    for s, e, lab in sorted(map(tuple, spans)):
        if out and out[-1][2] == lab and _SPACE.fullmatch(text[out[-1][1] : s]):
            out[-1][1] = e
        else:
            out.append([s, e, lab])
    return [tuple(x) for x in out]


def _joined(text: str, rec: dict) -> dict:
    return {**rec, "spans": [list(x) for x in join_words(text, rec["spans"])]}


def before_after(n: int, log_dir=store.LOG_DIR) -> dict[str, tuple[dict, dict]]:
    """Card id -> (gold before adjudication, gold after), for cards with at least one adjudication save."""
    before: dict[str, dict] = {}
    after: dict[str, dict] = {}
    path = store.log_path(n, log_dir)
    if not path.exists():
        return {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        cid = rec["id"]
        if rec.get("phase") == "schema":
            continue  # a rule applied to every card after the run (tools/golden/highway_alt.py), not adjudication
        if rec.get("void"):
            before.pop(cid, None)
            after.pop(cid, None)
        elif rec.get("phase") == "adjudicate" or cid in after:
            after[cid] = rec
        else:
            before[cid] = rec
    return {cid: (before[cid], rec) for cid, rec in after.items() if cid in before}


def _gold(rec: dict) -> tuple:
    return (
        sorted(map(tuple, rec["spans"])),
        sorted(json.dumps(a, sort_keys=True) for a in rec.get("alternatives", [])),
    )


def tally(cards: dict[str, str], pairs: dict[str, tuple[dict, dict]], readings: dict[str, dict[str, list]]) -> dict:
    """`cards` id -> text; `readings` parser -> id -> canonical spans (None when the parser failed)."""
    out = {"adjudicated": 0, "gold_changed": 0, "parsers": {}}
    for p in readings:
        out["parsers"][p] = {"questions_before": 0, "toward": 0, "away": 0, "cards_toward": 0, "cards_away": 0}
    for cid, (bef, aft) in pairs.items():
        if cid not in cards:
            continue
        bef, aft = _joined(cards[cid], bef), _joined(cards[cid], aft)
        out["adjudicated"] += 1
        if _gold(bef) == _gold(aft):
            for p, by in readings.items():
                if by.get(cid) is not None:
                    out["parsers"][p]["questions_before"] += len(disagreements(bef, by[cid]))
            continue
        out["gold_changed"] += 1
        for p, by in readings.items():
            spans = by.get(cid)
            if spans is None:
                continue
            q_bef = {(q["start"], q["end"], q["label"]) for q in disagreements(bef, spans)}
            q_aft = {(q["start"], q["end"], q["label"]) for q in disagreements(aft, spans)}
            t = out["parsers"][p]
            t["questions_before"] += len(q_bef)
            t["toward"] += len(q_bef - q_aft)
            t["away"] += len(q_aft - q_bef)
            t["cards_toward"] += bool(q_bef - q_aft)
            t["cards_away"] += bool(q_aft - q_bef)
    return out


def main(argv: list[str]) -> None:
    from adapters.registry import ADAPTERS

    rounds = [int(a) for a in argv] or ROUNDS
    adapters = {name: cls() for name, cls in sorted(ADAPTERS.items())}
    removed = store.removed_ids()
    total: dict = {}
    for n in rounds:
        try:
            cards = {c["id"]: c["text"] for c in store.load_round(n) if c["id"] not in removed}
            pairs = before_after(n)
        except Exception as e:  # reader errors can quote card text
            sys.exit(f"round {n}: {type(e).__name__}")
        readings: dict[str, dict[str, list]] = {}
        for name, ad in adapters.items():
            readings[name] = {}
            for cid in pairs:
                if cid not in cards:
                    continue
                try:
                    readings[name][cid] = join_words(
                        cards[cid], [(s.start, s.end, s.label) for s in ad.canonical(cards[cid])]
                    )
                except Exception:
                    readings[name][cid] = None
        t = tally(cards, pairs, readings)
        t["late_changes"] = len([c for c in store.late_changes(n) if c in cards])
        print(json.dumps({"round": n, **t}))
        total = _add(total, t)
    print(json.dumps({"round": "all", **total}))


def _add(a: dict, b: dict) -> dict:
    if not a:
        return json.loads(json.dumps(b))
    for k, v in b.items():
        a[k] = _add(a[k], v) if isinstance(v, dict) else a[k] + v
    return a


if __name__ == "__main__":
    main(sys.argv[1:])
