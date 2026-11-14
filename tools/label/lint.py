"""A typo check on the hand labels. It runs no parser, so it is safe to use while labeling is still going on.

    uv run python -m tools.label.lint            # every round with saves; prints counts and card ids per rule
    uv run python -m tools.label.lint 3 4        # only these rounds

Rules (each is a question about the card, never a verdict; it prints the rule and the card id, never the text):

- `state-unknown`: a `state` span that is not a US state, DC or territory code or name
- `zip-shape`: a `postal_code` span that is not 5 digits or ZIP+4
- `zip-state`: the ZIP's state (GeoNames postal list, doorplate's local-data) is not the labeled state
- `dir-shape`: a `street_pre_direction` or `street_post_direction` span that is not a direction word
- `dir-in-name`: a `street_name` that starts or ends with a direction word and has no direction span on that side
- `dir-side`: a pre-direction after the street name, or a post-direction before it
- `order`: street parts out of order (number, pre-direction, pre-type, name, post-type, post-direction), or city, state
  and ZIP out of order
- `uncovered`: a word or number outside every span (and outside every `none` alternative)
- `duplicate`: two spans of a label that occurs once (`state`, `postal_code`, the directions) on a card

Cards flagged `non_address` or `ambiguous` are skipped. A hit is a reason to look at the card again, not an error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.label import store

PLACES = Path.home() / "projects/temp-postal/doorplate/local-data/places/geonames-postal/us/US.txt"
STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "PR",
    "VI",
    "GU",
    "AS",
    "MP",
    "AA",
    "AE",
    "AP",
]  # noqa: E501
NAMES = {  # full names people spell out (labels allow them)
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA", "COLORADO": "CO",
    "CONNECTICUT": "CT", "DELAWARE": "DE", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME",
    "MARYLAND": "MD", "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS", "MISSOURI": "MO",
    "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV", "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM",
    "NEW YORK": "NY", "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK", "OREGON": "OR",
    "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC", "SOUTH DAKOTA": "SD", "TENNESSEE": "TN",
    "TEXAS": "TX", "UTAH": "UT", "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC", "PUERTO RICO": "PR",
}  # fmt: skip
DIRECTIONS = {
    "N", "S", "E", "W", "NE", "NW", "SE", "SW", "NORTH", "SOUTH", "EAST", "WEST",
    "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST", "NO", "SO",
}  # fmt: skip
ONCE = ("state", "postal_code", "street_pre_direction", "street_post_direction")  # a name or number may be split
STREET_ORDER = [
    "house_number_prefix",
    "house_number_value",
    "house_number_suffix",
    "street_pre_direction",
    "street_pre_type",
    "street_name",
    "street_post_type",
    "street_post_direction",
]
LAST_LINE = ["city", "state", "postal_code"]
WORD = re.compile(r"[A-Za-z0-9]+")


def _norm(s: str) -> str:
    return " ".join(re.sub(r"[.,]", " ", s).upper().split())


def load_zip_states(path: Path = PLACES) -> dict[str, set[str]]:
    """ZIP5 -> the state codes it is listed under (empty when the places file is missing)."""
    out: dict[str, set[str]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            f = line.split("\t")
            if len(f) > 4:
                out.setdefault(f[1], set()).add(f[4])
    return out


def lint_card(card: dict, zips: dict[str, set[str]] | None = None) -> list[str]:
    """The rules a saved card breaks (`card`: `text`, `spans`, `alternatives`, `flag`); empty when none."""
    if card.get("flag"):
        return []
    text, spans = card["text"], sorted(card["spans"])
    hits: list[str] = []
    by: dict[str, list[tuple[int, int]]] = {}
    for s, e, lab in spans:
        by.setdefault(lab, []).append((s, e))

    def val(lab):
        return [_norm(text[s:e]) for s, e in by.get(lab, [])]

    state = None
    for v in val("state"):
        if v in STATES or v in NAMES:
            state = NAMES.get(v, v)
        else:
            hits.append("state-unknown")
    for v in val("postal_code"):
        if not re.fullmatch(r"\d{5}(-?\d{4})?", v):
            hits.append("zip-shape")
        elif zips and state and v[:5] in zips and state not in zips[v[:5]]:
            hits.append("zip-state")
    for lab in ("street_pre_direction", "street_post_direction"):
        if any(v.replace(" ", "") not in DIRECTIONS for v in val(lab)):  # `N.E.` is NE
            hits.append("dir-shape")
    for s, e in by.get("street_name", []):
        words = _norm(text[s:e]).split()
        if len(words) > 1 and words[0] in DIRECTIONS and "street_pre_direction" not in by:
            hits.append("dir-in-name")
        if len(words) > 1 and words[-1] in DIRECTIONS and "street_post_direction" not in by:
            hits.append("dir-in-name")
    name = by.get("street_name")
    if name:
        if any(s > name[-1][0] for s, _ in by.get("street_pre_direction", [])):
            hits.append("dir-side")
        if any(s < name[0][0] for s, _ in by.get("street_post_direction", [])):
            hits.append("dir-side")
    for order in (STREET_ORDER, LAST_LINE):
        firsts = [(by[lab][0][0], i) for i, lab in enumerate(order) if lab in by]
        if [i for _, i in sorted(firsts)] != sorted(i for _, i in firsts):
            hits.append("order")
    if any(len(v) > 1 for lab, v in by.items() if lab in ONCE):
        hits.append("duplicate")
    free = [(a["start"], a["end"]) for a in card.get("alternatives", []) if "none" in a["labels"]]
    for m in WORD.finditer(text):
        if not any(s <= m.start() and m.end() <= e for s, e, _ in spans) and not any(
            s <= m.start() and m.end() <= e for s, e in free
        ):
            hits.append("uncovered")
            break
    return list(dict.fromkeys(hits))


def main(argv: list[str]) -> int:
    rounds = [int(a) for a in argv] or list(range(1, 12))
    zips = load_zip_states()
    if not zips:
        print(f"(no ZIP list at {PLACES}: the zip-state rule is skipped)")
    total = 0
    for n in rounds:
        try:
            cards, log = store.load_round(n), store.load_log(n)
        except SystemExit:
            continue
        saved = [
            (c, log[c["id"]]) for c in cards if c["id"] in log and log[c["id"]].get("th") == store.text_hash(c["text"])
        ]
        found: dict[str, list[str]] = {}
        for c, rec in saved:
            for rule in lint_card({"text": c["text"], **rec}, zips):
                found.setdefault(rule, []).append(c["id"])
        if not saved:
            continue
        print(
            f"round {n}: {len(saved)} labeled cards; "
            + (", ".join(f"{k} {len(v)}" for k, v in sorted(found.items())) or "no hits")
        )
        for rule, ids in sorted(found.items()):
            print(f"  {rule}: {' '.join(ids)}")
        total += sum(len(v) for v in found.values())
    print(f"{total} hits in all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
