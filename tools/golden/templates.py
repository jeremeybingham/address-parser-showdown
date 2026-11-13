"""Hand templates for the golden set: real address shapes, invented values.

Every street name and number is made up here from syllables and a seeded generator. Only the (city, state, ZIP)
triples are real, read from the public GeoNames postal file. Parser output is never consulted: a shape is chosen by
its weight in `SHAPES` and by the seed alone (METHODOLOGY.md).
"""

from __future__ import annotations

import random

ONSETS = [
    "b",
    "br",
    "c",
    "ch",
    "d",
    "f",
    "g",
    "gl",
    "h",
    "j",
    "k",
    "l",
    "m",
    "n",
    "p",
    "pl",
    "r",
    "s",
    "st",
    "t",
    "v",
    "w",
]
VOWELS = ["a", "e", "i", "o", "u", "ae", "ia", "ou"]
CODAS = ["", "", "", "l", "n", "r", "s", "t", "m"]
TYPES = [  # (full, usps abbreviation)
    ("Street", "St"),
    ("Avenue", "Ave"),
    ("Road", "Rd"),
    ("Drive", "Dr"),
    ("Lane", "Ln"),
    ("Court", "Ct"),
    ("Boulevard", "Blvd"),
    ("Circle", "Cir"),
    ("Way", "Way"),
    ("Place", "Pl"),
    ("Trail", "Trl"),
    ("Terrace", "Ter"),
]
DIRS = [
    ("North", "N"),
    ("South", "S"),
    ("East", "E"),
    ("West", "W"),
    ("Northeast", "NE"),
    ("Northwest", "NW"),
    ("Southeast", "SE"),
    ("Southwest", "SW"),
]
UNITS = [
    ("Apartment", "Apt"),
    ("Suite", "Ste"),
    ("Unit", "Unit"),
    ("Building", "Bldg"),
    ("Floor", "Fl"),
    ("Room", "Rm"),
    ("Lot", "Lot"),
    ("Trailer", "Trlr"),
]
PEOPLE = ["Alder", "Briar", "Corwin", "Dellmar", "Eskin", "Farrow", "Garrick", "Halden", "Ismay", "Jorvik"]


def read_places(path) -> list[tuple[str, str, str]]:
    """(city, state, zip5) from a GeoNames postal file (tab separated; fields 1, 2 and 4)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) > 4 and p[1].isdigit() and len(p[1]) == 5 and len(p[4]) == 2:
                out.append((p[2], p[4], p[1]))
    return out


def name(r: random.Random) -> str:
    word = "".join(r.choice(ONSETS) + r.choice(VOWELS) + r.choice(CODAS) for _ in range(r.choice([2, 2, 2, 3])))
    return word.capitalize()


def number(r: random.Random) -> str:
    return str(r.choice([r.randint(1, 99), r.randint(100, 999), r.randint(1000, 9999), r.randint(10000, 99999)]))


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def street_core(r: random.Random, abbr: bool) -> str:
    base = ordinal(r.randint(1, 120)) if r.random() < 0.15 else name(r)
    if r.random() < 0.15:
        base = f"{name(r)} {name(r)}"
    full, short = r.choice(TYPES)
    t = short if abbr else full
    pre = post = ""
    if r.random() < 0.25:
        d = r.choice(DIRS)
        pre = (d[1] if abbr else d[0]) + " "
    elif r.random() < 0.1:
        d = r.choice(DIRS)
        post = " " + (d[1] if abbr else d[0])
    return f"{pre}{base} {t}{post}"


def unit(r: random.Random, abbr: bool) -> str:
    full, short = r.choice(UNITS)
    val = r.choice(
        [
            str(r.randint(1, 40)),
            f"{r.randint(1, 30)}{r.choice('ABCDEF')}",
            r.choice("ABCDEFGH"),
            f"{r.randint(1, 9)}-{r.choice('ABCD')}",
            str(r.randint(100, 950)),
        ]
    )
    if r.random() < 0.3:
        return f"#{val}"
    return f"{short if abbr else full}{r.choice(['', '.']) if abbr else ''} {val}"


def last_line(r: random.Random, place, form: str) -> str:
    city, state, zip5 = place
    zipv = zip5 + (f"-{r.randint(1000, 9999)}" if r.random() < 0.15 else "")
    if form == "nozip":
        return f"{city}, {state}"
    if form == "nostate":
        return f"{city} {zipv}"
    return f"{city}, {state} {zipv}"


def typo(r: random.Random, s: str) -> str:
    """One character slip in a word of five letters or more (drop, swap or double)."""
    words = s.split(" ")
    idx = [i for i, w in enumerate(words) if len(w) >= 5 and w.isalpha()]
    if not idx:
        return s
    i = r.choice(idx)
    w, j = words[i], r.randint(1, len(words[i]) - 2)
    kind = r.choice(["drop", "swap", "double"])
    w = (
        w[:j] + w[j + 1 :]
        if kind == "drop"
        else w[:j] + w[j + 1] + w[j] + w[j + 2 :]
        if kind == "swap"
        else w[:j] + w[j] + w[j:]
    )
    words[i] = w
    return " ".join(words)


# Each shape returns (line1 parts, wants_unit_line) via `build`; the weights are fixed here, before labeling.
def _po_box(r, abbr):
    word = r.choice(
        ["PO Box", "P.O. Box", "P O Box", "POB", "Post Office Box", "Box", "PO BOX", "P.O.Box", "P. O. Box"]
    )
    return f"{word} {r.randint(1, 9999)}"


def _rural(r, abbr):
    return r.choice(
        [
            f"RR {r.randint(1, 9)} Box {r.randint(1, 300)}",
            f"Rural Route {r.randint(1, 9)} Box {r.randint(1, 99)}{r.choice(['', 'A', 'B'])}",
            f"R.R. {r.randint(1, 9)} Box {r.randint(1, 300)}",
            f"HC {r.randint(1, 80)} Box {r.randint(1, 400)}",
            f"Star Route {r.randint(1, 20)} Box {r.randint(1, 99)}",
            f"RFD {r.randint(1, 9)} Box {r.randint(1, 99)}",
        ]
    )


def _highway(r, abbr):
    n = r.randint(1, 999)
    return r.choice(
        [
            f"{number(r)} State Highway {n}",
            f"{number(r)} US Hwy {n}",
            f"{number(r)} County Road {n}",
            f"{number(r)} CR {n}",
            f"{number(r)} FM {n}",
            f"{number(r)} State Route {n} {r.choice(['N', 'S', 'E', 'W'])}",
            f"{number(r)} Hwy {n}",
            f"{number(r)} Interstate {r.randint(5, 95)} Frontage Rd",
            f"{number(r)} Co Rd {n}{r.choice(['', 'A'])}",
        ]
    )


def _fraction(r, abbr):
    return f"{r.randint(1, 999)} {r.choice(['1/2', '1/4', '3/4'])} {street_core(r, abbr)}"


def _letter(r, abbr):
    n, c = r.randint(1, 999), r.choice("ABCDEFGH")
    return f"{n}{c} {street_core(r, abbr)}" if r.random() < 0.5 else f"{n} {c} {street_core(r, abbr)}"


def _hyphen(r, abbr):
    return r.choice(
        [
            f"{r.randint(1, 99)}-{r.randint(1, 99)} {street_core(r, abbr)}",
            f"{r.choice('NSEW')}{r.randint(1, 99)}{r.choice('NSEW')}{r.randint(1000, 99999)} {street_core(r, abbr)}",
        ]
    )


def _plain(r, abbr):
    return f"{number(r)} {street_core(r, abbr)}"


def _directional(r, abbr):
    d = r.choice(DIRS)
    d = d[1] if abbr else d[0]
    full, short = r.choice(TYPES)
    t = short if abbr else full
    core = f"{d} {name(r)} {t}" if r.random() < 0.6 else f"{name(r)} {t} {d}"
    return f"{number(r)} {core}"


def _care_of(r, abbr):
    return f"c/o {r.choice(PEOPLE)} {name(r)}, {_plain(r, abbr)}"


def _highrise(r, abbr):
    return f"{_plain(r, abbr)} {unit(r, abbr)}"


def _general_delivery(r, abbr):
    return "General Delivery"


SHAPES = [  # (name, weight, builder, takes unit suffix)
    ("street-unit", 20, _highrise, False),
    ("po-box", 15, _po_box, False),
    ("rural-route", 8, _rural, False),
    ("highway", 12, _highway, False),
    ("directional", 8, _directional, False),
    ("fraction", 4, _fraction, False),
    ("number-letter", 6, _letter, False),
    ("hyphen-number", 4, _hyphen, False),
    ("care-of", 3, _care_of, False),
    ("general-delivery", 2, _general_delivery, False),
    ("street-plain", 18, _plain, False),
]
MODS = [("none", 40), ("typo", 12), ("upper", 18), ("lower", 6), ("nocomma", 14), ("nozip", 5), ("nostate", 5)]


def one(r: random.Random, places) -> tuple[str, str, str]:
    """(text, shape, modifier) for one record."""
    shape, _, build, _ = r.choices(SHAPES, weights=[s[1] for s in SHAPES])[0]
    mod = r.choices([m[0] for m in MODS], weights=[m[1] for m in MODS])[0]
    abbr = r.random() < 0.7
    line1 = build(r, abbr)
    if shape == "street-plain" and r.random() < 0.25:
        line1 += " " + unit(r, abbr)
    place = r.choice(places)
    form = mod if mod in ("nozip", "nostate") else "full"
    last = last_line(r, place, form)
    if shape == "general-delivery":
        line1 = "General Delivery"
    text = f"{line1}, {last}"
    if mod == "typo":
        text = typo(r, text)
    elif mod == "nocomma":
        text = text.replace(",", "")
    elif mod == "upper":
        text = text.upper()
    elif mod == "lower":
        text = text.lower()
    return text, shape, mod


def make(r: random.Random, places, n: int) -> list[tuple[str, str, str]]:
    return [one(r, places) for _ in range(n)]
