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
    covered: str = ""  # `nightmare` only: the form a closed rule or fixed report handles (variant `covered`)
    adjacent: str = ""  # `nightmare` only: a nearby form an open issue leaves out (variant `adjacent`)
    source: str = ""  # `nightmare` only: the issues the two variants come from (docs/research/nightmare-survey.md)

    @property
    def variants(self) -> tuple[str, ...]:
        """`covered` and `adjacent` for a paired class, `neutral` for every other tier."""
        return ("covered", "adjacent") if self.tier == "nightmare" else ("neutral",)


def _n(origin: str, doc: str, covered: str, adjacent: str, source: str) -> ShapeClass:
    return ShapeClass("nightmare", origin, doc, covered, adjacent, source)


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
    # Round 8 (`nightmare`): every class is paired (issue #22, docs/research/nightmare-survey.md). `covered` is the form a
    # closed rule or fixed report handles; `adjacent` is a nearby form an open issue leaves out. Tags come from the
    # issue text only; no parser is run, and a tag is never changed after a scored run. All strings are invented.
    # From doorplate's 0.5.x and 0.6.x rule research (D# = jeremeybingham/doorplate issues, U# = datamade/usaddress,
    # L# = openvenues/libpostal):
    "second-number": _n(
        "doorplate-research",
        "a second number after the house number",
        "a building and a unit (`31 208 Birch Ln`), or a close same-parity pair (`7310 7312 Oak Dr`)",
        "two numbers joined by `&` (`3 & 5 E 41st St`)",
        "D#590 D#591 D#274 D#617 L#85 L#151",
    ),
    "letter-before-street": _n(
        "doorplate-research",
        "a lone letter before the street name",
        "a letter A to D as a unit (`46 B Linden Ave`)",
        "a letter outside A to D, then a direction letter, an initial (`9311 J W Clay Blvd`); a letter before the number",
        "D#487 D#270 D#360 D#312 U#245",
    ),
    "no-so-direction": _n(
        "doorplate-research",
        "`NO` and `SO` for north and south",
        "`464 NO Maple Ave`, `84 Elmhurst Pl SO`",
        "`County Rd SO` with no number; a street named for a direction (`250 South St E`)",
        "D#470 D#269 D#643 U#402 L#353",
    ),
    "county-road-compass": _n(
        "doorplate-research",
        "a county road with a compass pair",
        "`4410 County Road SE 1234`; `88 East TR 56`",
        "`<Name> Road <n>` outside the closed list; `Farm Road 1110`; `RM 1431`; `S East Loop 410`",
        "D#642 D#388 D#593 U#315 U#247 U#364",
    ),
    "zip4-cut": _n(
        "doorplate-research",
        "a ZIP+4 cut short (`33601-12`)",
        "`33601-12` and `3360112` repaired to the ZIP",
        "a ZIP+4 with a space (`33000 1234`); a lost leading zero with a spaced +4; ZIP before state",
        "D#275 D#606 D#519 L#382",
    ),
    "unit-before-street": _n(
        "doorplate-research",
        "the unit before the street (`Apt 4 12 Oak St`)",
        "a suffix word follows the unit value (`12-40 Suite 9 Delmar Blvd`)",
        "no suffix word (`242 Apt B Example`); `Apt S` plus street with the value on line 2",
        "D#296 D#529 D#498 U#208 L#671",
    ),
    "paren-unit": _n(
        "doorplate-research",
        "a unit in parentheses (`12 Oak St (Unit 4)`)",
        "a floor or unit at the edge of a segment (`12 Elm St (3rd Fl)`)",
        "a parenthesized group that is not a unit (`(Rear Entrance)`); a parenthesis inside a name",
        "D#291 D#516 D#644 D#645 L#580",
    ),
    # From outside doorplate (Pub 28, usaddress and libpostal reports, and the doorplate leftovers they share).
    "military": _n(
        "outside",
        "a military address (`PSC 1234 Box 56, APO AE 09012`; Pub 28)",
        "the Pub 28 form",
        "the military and State Department forms Pub 28 shows only as images",
        "Pub 28; D#92. Thin: no usaddress or libpostal report",
    ),
    "urbanization": _n(
        "outside",
        "a Puerto Rico urbanization line (`URB Las Flores`; Pub 28)",
        "`URB` on its own line before the street (Pub 28)",
        "`URB` after the street (`27 Calle Luna URB Las Palmas`); street-first forms",
        "Pub 28; D#318 D#319 D#314. Thin: covered form from Pub 28 only",
    ),
    "grid-utah": _n(
        "outside",
        "a grid address with two directionals (`123 E 400 S`; Pub 28)",
        "`640 E 3780 S` with a plain direction",
        "`640 E 3780 SO`; a grid system the schema has no field for",
        "D#269 L#295",
    ),
    "grid-wisconsin": _n(
        "outside",
        "a letter-and-digits number twice before the name (`N45 W2210 Oak Ave`)",
        "`W148 N9748 Tree Tops Dr` (usaddress reads both as the number)",
        "the same form where doorplate leaves the second part in the street name",
        "U#92 D#311 D#242",
    ),
    "spelled-number": _n(
        "outside",
        "a house number in words (`One Oak Plaza`)",
        "a spelled number before a name that starts with a suffix word (`One Marlow Park Ave`)",
        "a lone `One` on line 2; a spelled number with commas (`Twelve, Elm St`); a spelled-out street",
        "D#221 D#559 D#601 U#194",
    ),
    "intersection": _n(
        "outside",
        "two streets and no number (`Oak St & 3rd Ave`)",
        "`&` inside a street name (`1176 Town & Country Cmns`); `72 Rolfe & Arcadia Ave`",
        "`Oak St / 3rd Ave` with a slash; a building name with an intersection",
        "U#85 L#84 U#218 U#230 U#312 U#357",
    ),
    "highway-lettered": _n(
        "outside",
        "a lettered or directional route (`State Route 9W`)",
        "`United States Highway 27`; `State Rd QQ` keeps its letters; `Business` routes",
        "`Old United States Highway 41-45`; a lot on a state highway (`Lot 2-B MN Hwy 108`); several highways",
        "D#543 D#589 U#186 D#608 L#452 U#206",
    ),
    "non-address-nightmare": _n(
        "outside",
        "a string with an address-like look that is not one",
        "a placeholder in the street field (`No Address On File`); `NaN` in the city",
        "boilerplate before the street; a foreign address; a prison inmate line",
        "D#273 D#419 D#483 D#361 U#239 U#262",
    ),
    "box-glued": _n(
        "outside",
        "a box or route word glued to its number or letter",
        "`Campus Box 4521`; a place called Box Elder after `PO Box`",
        "`POBOX481`, `HCR75 BOX 12D`, `PO Drawer C`, `PO Box NA`",
        "D#373 D#384 U#124 D#304 D#598 D#358 L#21",
    ),
    "fraction-form": _n(
        "outside",
        "a half or quarter written in a form that is not `1/2`",
        "a half with no slash (`1 2 N Main St`)",
        "a Unicode fraction (`537½ W 26th St`); `4422 1/4 Lincoln Ave`",
        "D#247 D#387 L#191 U#151",
    ),
    "lot-trailer-site": _n(
        "outside",
        "a lot, pier, trailer or site word after the street",
        "`Pier 39 Lot 12`",
        "`5th Street Trailer 30`; `Lot 2-B MN Hwy 108`; a pier ending a street name; `Msc 518` after the street",
        "U#139 U#349 L#452 D#327 D#375",
    ),
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
