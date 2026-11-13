"""The adjudication queue: where any parser reads a labeled card differently from the gold.

Run only after a round is fully labeled (it runs the parsers; labeling never does). The queue holds, per card, the
other readings as `{start, end, label}` with no parser name, so the owner decides blind: keep the gold, or change it.

    uv run python -m tools.label.adjudicate ROUND [ROUND...]    # writes local-data/labels/adjudication.jsonl
"""

import json
import sys

from schema import coarse, fine_parts
from tools.label import store


def _gold_coarse(gold: list[list]) -> set[tuple[int, int, str]]:
    """Per coarse field, the range from its first fine span to its last (how a parser that cannot split reads it)."""
    by: dict[str, list[list]] = {}
    for s, e, lab in gold:
        by.setdefault(coarse(lab), []).append([s, e])
    return {(min(s for s, _ in v), max(e for _, e in v), f) for f, v in by.items()}


def disagreements(card: dict, parser_spans: list[tuple[int, int, str]]) -> list[dict]:
    """Parser spans (canonical labels) the gold does not hold, as questions. Coarse labels from a parser that cannot
    split a field agree when they cover the gold's whole field. Alternatives recorded on the card count as agreement."""
    gold = {tuple(sp) for sp in card["spans"]}
    for alt in card.get("alternatives", []):
        gold |= {(alt["start"], alt["end"], lab) for lab in alt["labels"]}
    gold_coarse = _gold_coarse(card["spans"])
    out = []
    for s, e, lab in parser_spans:
        if (s, e, lab) in gold:
            continue
        if fine_parts(lab) and (s, e, lab) in gold_coarse:
            continue
        out.append({"start": s, "end": e, "label": lab})
    return out


def build_queue(rounds: list[int], adapters: dict | None = None) -> list[dict]:
    """One entry per card with at least one question; the same reading from two parsers is asked once."""
    if adapters is None:
        from adapters.registry import ADAPTERS

        adapters = {name: cls() for name, cls in ADAPTERS.items()}
    queue = []
    for n in rounds:
        for card in store.gold_cards(n):
            if not card["labeled"]:
                raise store.CardError(f"round {n} has unlabeled cards; label it first")
            seen: dict[tuple, dict] = {}
            for ad in adapters.values():
                try:
                    spans = [(sp.start, sp.end, sp.label) for sp in ad.canonical(card["text"])]
                except Exception:  # a parser that fails has no reading to ask about
                    continue
                for q in disagreements(card, spans):
                    seen.setdefault((q["start"], q["end"], q["label"]), q)
            if seen:
                queue.append(
                    {"round": n, "id": card["id"], "questions": sorted(seen.values(), key=lambda q: q["start"])}
                )
    return queue


def main(argv: list[str]) -> None:
    rounds = [int(a) for a in argv] or list(range(1, 7))
    try:
        queue = build_queue(rounds)
    except store.CardError as e:
        sys.exit(str(e))
    store.LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = store.LOG_DIR / "adjudication.jsonl"
    path.write_text("".join(json.dumps(q) + "\n" for q in queue))
    print(f"{len(queue)} cards with a different reading, {sum(len(q['questions']) for q in queue)} questions")


if __name__ == "__main__":
    main(sys.argv[1:])
