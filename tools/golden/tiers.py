"""Difficulty tiers of the golden set (issue #14): the shape-class table, the tagger and the `normal` mapping check.

    uv run python -m tools.golden.tiers      # counts per tier and shape class for the exported gold rounds

A record's tier comes from its **shape class** and nothing else (`sets/golden/COMPOSITION.md`, "Difficulty tiers"):

- A template record's class is the shape it was written from (`provenance.jsonl`); a typo modifier makes it `typo`.
- A public or clean record has no written shape (`as-found`, `ordinary`), so its class is read from its **gold** spans by
  the rules in `class_from_gold`. Gold is the owner's blind labeling; no parser output is read here.
- Rounds 7 and 8 (drawn after this table is committed) carry their class in `provenance.jsonl` like the templates.

Then the `normal` check: a record whose class says `normal` stays there only if its gold uses core fields alone, every
gold label's coarse field is something each parser's mapping file can produce, the card is not `doubtful` and has no
flag. Otherwise it moves up to `hard` (never dropped). This proves the 100% ceiling from the mapping files, without
running a parser. A record with a `non_address` or `ambiguous` flag keeps its tier; the scorer reports it apart.
"""

from __future__ import annotations

import collections
import json
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from adapters.base import Mapping
from schema import coarse, labels

ROOT = Path(__file__).resolve().parents[2]
PROVENANCE = ROOT / "sets" / "golden" / "provenance.jsonl"
GOLD_DIR = ROOT / "sets" / "golden" / "gold"
PARSERS = ("doorplate", "usaddress", "libpostal")
TIERS = ("normal", "hard", "nightmare")
FLAGS = ("non_address", "ambiguous")


@dataclass(frozen=True)
class ShapeClass:
    tier: str
    origin: str  # "base" (rounds 1 to 6), "doorplate-research" or "outside" (for `nightmare`, see COMPOSITION.md)
    doc: str


# The class-to-tier table. Fixed before rounds 7 and 8 are drawn; a change is a PR that says why.
# Every example below is invented.
CLASSES: dict[str, ShapeClass] = {
    # Rounds 1 to 6: the template shapes (templates.py) and the classes read from gold for public and clean records.
    "street-plain": ShapeClass("normal", "base", "number, street, no unit (`12 Oak St`)"),
    "ordinary": ShapeClass("normal", "base", "the clean stratum: number, plain street, city, state, ZIP"),
    "street-unit": ShapeClass("normal", "base", "a street address with one unit (`12 Oak St Apt 4`, `#4`)"),
    "directional": ShapeClass("normal", "base", "a pre or post directional (`12 N Oak St`, `12 Oak St NW`)"),
    "number-letter": ShapeClass("normal", "base", "a letter after the number, joined or apart (`12B`, `12 B Oak St`)"),
    "po-box": ShapeClass("normal", "base", "a PO box in any spelling, no street"),
    "highway": ShapeClass("normal", "base", "a numbered highway or county road (`12 US Hwy 41`, `12 CR 7`)"),
    "fraction": ShapeClass("hard", "base", "a fraction after the number (`12 1/2 Oak St`)"),
    "hyphen-number": ShapeClass("hard", "base", "a hyphenated or grid number (`12-34 Oak St`, `N12W3456 Oak St`)"),
    "rural-route": ShapeClass("hard", "base", "a rural, highway-contract or star route with a box"),
    "care-of": ShapeClass("hard", "base", "a care-of name before the street"),
    "general-delivery": ShapeClass("hard", "base", "`General Delivery` in place of a street"),
    "typo": ShapeClass("hard", "base", "any shape with a one-character slip"),
    "box-and-street": ShapeClass("hard", "base", "a street and a PO box in one record"),
    "named-place": ShapeClass("hard", "base", "a building name, a recipient or text the schema has no field for"),
    "no-street": ShapeClass("hard", "base", "no street, box or route at all (a city and state only, a stray word)"),
    # Round 7 (`hard`, added): rarer shapes and observed typo classes on invented values.
    "typo-glued": ShapeClass("hard", "base", "two words run together (`12 OakSt`, `Tampa,FL`)"),
    "typo-type": ShapeClass("hard", "base", "a slip in the street type or unit word (`Stret`, `Aptt`)"),
    "zip4-plain": ShapeClass("hard", "base", "a ZIP+4 with no hyphen (`336011234`)"),
    "state-spelled": ShapeClass("hard", "base", "the state written out (`Tampa, Florida 33601`)"),
    "two-units": ShapeClass("hard", "base", "two units (`Bldg 3 Apt 12`)"),
    "pre-type": ShapeClass("hard", "base", "a type before the name (`12 Avenue C`, `12 Calle Sol`)"),
    "non-address-hard": ShapeClass("hard", "base", "a string that is not an address (`Same as above`); flagged"),
    # Round 8 (`nightmare`): shape classes from doorplate's 0.5.x and 0.6.x rule research. The strings are invented.
    "second-number": ShapeClass("nightmare", "doorplate-research", "a second number after the house number"),
    "letter-before-street": ShapeClass("nightmare", "doorplate-research", "a lone letter before the street name"),
    "no-so-direction": ShapeClass("nightmare", "doorplate-research", "`NO` and `SO` for north and south"),
    "county-road-compass": ShapeClass("nightmare", "doorplate-research", "a county road with a compass pair"),
    "zip4-cut": ShapeClass("nightmare", "doorplate-research", "a ZIP+4 cut short (`33601-12`)"),
    "unit-before-street": ShapeClass(
        "nightmare", "doorplate-research", "the unit before the street (`Apt 4 12 Oak St`)"
    ),
    "paren-unit": ShapeClass("nightmare", "doorplate-research", "a unit in parentheses (`12 Oak St (Unit 4)`)"),
    # Round 8 (`nightmare`): shape classes from outside doorplate (USPS Publication 28 and common real-world forms).
    "military": ShapeClass("nightmare", "outside", "a military address (`PSC 1234 Box 56, APO AE 09012`; Pub 28)"),
    "urbanization": ShapeClass("nightmare", "outside", "a Puerto Rico urbanization line (`URB Las Flores`; Pub 28)"),
    "grid": ShapeClass("nightmare", "outside", "a grid address with two directionals (`123 E 400 S`; Pub 28)"),
    "spelled-number": ShapeClass("nightmare", "outside", "a house number in words (`One Oak Plaza`)"),
    "intersection": ShapeClass("nightmare", "outside", "two streets and no number (`Oak St & 3rd Ave`)"),
    "highway-lettered": ShapeClass("nightmare", "outside", "a lettered or directional route (`State Route 9W`)"),
    "milepost": ShapeClass("nightmare", "outside", "a mile marker or no house number on a highway"),
    "non-address-nightmare": ShapeClass("nightmare", "outside", "a string with an address-like look that is not one"),
}


@cache
def reachable(parser: str) -> frozenset[str]:
    """The coarse fields a parser's mapping file can produce (`other` excluded)."""
    return frozenset(coarse(t) for t in Mapping(parser).claims)


def mapping_ok(spans: list[list], parsers: tuple[str, ...] = PARSERS) -> bool:
    """Every gold span is a core label whose coarse field each parser can produce: 100% is possible for all."""
    known = labels()
    for _, _, lab in spans:
        field = coarse(lab)
        if known[field].scope != "core" or any(field not in reachable(p) for p in parsers):
            return False
    return True


def class_from_gold(spans: list[list]) -> str:
    """The shape class of a record with no written shape, from the coarse fields and labels of its gold."""
    labs = {lab for _, _, lab in spans}
    fields = {coarse(lab) for lab in labs}
    if fields & {"recipient", "building_name", "country", "other"}:
        return "named-place"
    if "route" in fields:
        return "rural-route"
    if "po_box" in fields:
        return "box-and-street" if "street" in fields else "po-box"
    if "street" not in fields:
        return "no-street"
    if sum(lab == "unit_type" for _, _, lab in spans) > 1:
        return "two-units"
    if labs & {"house_number_prefix", "house_number_suffix"}:
        return "number-letter"
    if "unit" in fields:
        return "street-unit"
    if labs & {"street_pre_direction", "street_post_direction"}:
        return "directional"
    return "street-plain"


def shape_class(prov: dict, spans: list[list]) -> str:
    """The class of one record: the written shape for templates and added rounds, else read from gold."""
    shape = prov.get("shape", "")
    if prov.get("style") == "typo":
        return "typo"
    if shape in ("as-found", "ordinary"):
        cls = class_from_gold(spans)
        return "ordinary" if shape == "ordinary" and cls == "street-plain" else cls
    if shape not in CLASSES:
        raise KeyError(f"{prov.get('id')}: shape {shape!r} is not in the class table")
    return shape


def tier_of(prov: dict, card: dict) -> tuple[str, str, bool]:
    """(tier, shape class, moved up by the mapping check) for one labeled card."""
    cls = shape_class(prov, card["spans"])
    tier = CLASSES[cls].tier
    if tier == "normal" and (card.get("doubtful") or card.get("flag") or not mapping_ok(card["spans"])):
        return "hard", cls, True
    return tier, cls, False


def load_provenance(path: Path = PROVENANCE) -> dict[str, dict]:
    return {r["id"]: r for r in (json.loads(x) for x in path.read_text().splitlines() if x.strip())}


def load_gold(gold_dir: Path = GOLD_DIR) -> list[dict]:
    out = []
    for path in sorted(gold_dir.glob("round-*.jsonl")):
        out += [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    return out


def summary(gold: list[dict], prov: dict[str, dict]) -> dict:
    """Counts per tier, per (tier, class), moved up by the mapping check, and flagged (counts only)."""
    tiers, classes, moved, flags = (
        collections.Counter(),
        collections.Counter(),
        collections.Counter(),
        collections.Counter(),
    )
    for card in gold:
        tier, cls, up = tier_of(prov[card["id"]], card)
        tiers[tier] += 1
        classes[(tier, cls)] += 1
        moved[cls] += up
        if card.get("flag"):
            flags[(tier, card["flag"])] += 1
    return {"tiers": tiers, "classes": classes, "moved": +moved, "flags": flags}


def main() -> None:
    gold = load_gold()
    if not gold:
        sys.exit("no exported gold rounds in sets/golden/gold/ yet")
    s = summary(gold, load_provenance())
    print(f"{len(gold)} records: " + ", ".join(f"{t} {s['tiers'][t]}" for t in TIERS))
    for (tier, cls), n in sorted(s["classes"].items()):
        print(f"  {tier:9} {cls:22} {n:5}  moved up by the mapping check: {s['moved'].get(cls, 0)}")
    for (tier, flag), n in sorted(s["flags"].items()):
        print(f"  flagged {flag} in {tier}: {n}")


if __name__ == "__main__":
    main()
