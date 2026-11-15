"""Add the schema's street reading of a numbered highway as an accepted alternative (decided 2026-11-15, after run 1).

`schema/schema.toml` reads a highway as a street (`US` or `State` is `street_pre_type`, the number is the
`street_name`); `route` is for rural, highway contract and military routes. Some golden cards label a highway
(`US HWY 74`, `STATE ROUTE 9`, `COUNTY ROAD 12`) as `route_type` and `route_value`. This keeps that reading and adds the
schema's: one alternative over the whole run of route spans, labeled `street_name`, the form used where the labeler
added it by hand. A run of route spans is a highway unless one of its type words is a rural, highway contract or
military word (`RURAL_WORDS`) or it has a box (`route_box_*`). The rule reads the gold only; no parser is run.

It appends one save per card to the label log (phase `schema`; the log is never rewritten), so export and derive
carry the alternative to the private and the shipped gold:

    uv run python -m tools.golden.highway_alt            # dry run: counts per round
    uv run python -m tools.golden.highway_alt --confirm  # append the saves; then export and derive every round
"""

from __future__ import annotations

import re
import sys

from tools.label import store

RURAL_WORDS = re.compile(
    r"(?i)^(r\.?\s*r\.?|rural|rfd|r\.?f\.?d\.?|hc|hcr|star|psc|cmr|unit|uss|box|contract)$"
)  # rural route, highway contract, star route, military
ROUTE = {"route_type", "route_value"}
ROUNDS = range(1, 13)


def route_runs(text: str, spans: list[list]) -> list[list[list]]:
    """Runs of neighbouring route spans (any `route*` label) with only spaces, commas or dashes between them."""
    runs: list[list[list]] = []
    for sp in sorted(spans):
        if not sp[2].startswith("route"):
            continue
        if runs and re.fullmatch(r"[\s,\-]*", text[runs[-1][-1][1] : sp[0]]):
            runs[-1].append(sp)
        else:
            runs.append([sp])
    return runs


def highway_alternatives(card: dict) -> list[dict]:
    """The alternatives to add to one card (empty when it has no highway, or already accepts this reading)."""
    text = card["text"]
    have = {(a["start"], a["end"]) for a in card.get("alternatives", [])}
    out = []
    for run in route_runs(text, card["spans"]):
        if any(sp[2] not in ROUTE for sp in run):
            continue  # a box: a rural or contract route
        words = [w for sp in run if sp[2] == "route_type" for w in text[sp[0] : sp[1]].split()]
        if any(RURAL_WORDS.match(w.strip(".,")) for w in words):
            continue
        start, end = run[0][0], run[-1][1]
        if any(s <= start and end <= e for s, e in have):
            continue
        out.append({"start": start, "end": end, "labels": ["street_name"]})
    return out


def main(argv: list[str]) -> None:
    confirm = "--confirm" in argv
    removed = store.removed_ids()
    total = 0
    for n in ROUNDS:
        try:
            cards = [c for c in store.gold_cards(n) if c["labeled"] and c["id"] not in removed]
            latest = store.load_log(n)
        except Exception as e:  # reader errors can quote card text
            sys.exit(f"round {n}: {type(e).__name__}")
        hits = [(c, highway_alternatives(c)) for c in cards]
        hits = [(c, alts) for c, alts in hits if alts]
        total += len(hits)
        print(f"round {n}: {len(hits)} cards, {sum(len(a) for _, a in hits)} alternatives")
        if confirm:
            for c, alts in hits:
                rec = latest[c["id"]]
                payload = {k: rec.get(k, d) for k, d in store.CARD_FIELDS.items() if k != "phase"}
                payload["alternatives"] = rec.get("alternatives", []) + alts
                store.save_card(n, c, payload, phase="schema")
    print(f"{total} cards" + ("; saved" if confirm else " (dry run; --confirm saves)"))


if __name__ == "__main__":
    main(sys.argv[1:])
