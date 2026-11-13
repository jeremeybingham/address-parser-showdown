#!/usr/bin/env python3
"""Draw round 8 (`nightmare`, issue #22): invented strings for each paired class, equal numbers per variant.

    uv run python -m tools.golden.nightmare             # the plan, and a dry draw with the cap and exclusion checks
    uv run python -m tools.golden.nightmare --confirm   # writes sets/golden/rounds/round-8.jsonl (public seed)
    uv run python -m tools.golden.nightmare --confirm --twin   # the private twin (unpublished seed), doorplate's local-data
    uv run python -m tools.golden.nightmare --check     # redraw and compare with the committed round and provenance

Every class in `tiers.CLASSES` with tier `nightmare` has FORMS[class]["covered"] and ["adjacent"]: builders that make one
invented line from a seeded generator. The tracker letter of a form says where its shape came from (D doorplate, U
usaddress, L libpostal, P Publication 28; `docs/research/nightmare-survey.md`). Forms are dealt round-robin, so a cell
(class, variant) gets its forms in near-equal numbers. No parser is run; the variant is set by the form that wrote the
string. Only the (city, state, ZIP) triples are real (GeoNames). Rounds 1 to 6 are never touched.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.golden import exclusions, templates  # noqa: E402
from tools.golden.tiers import CLASSES  # noqa: E402

PUBLIC_SEED = 20261113
PER_CELL = 9  # records per (class, variant) unless SIZE says otherwise; both variants of a class always get the same
# Sizes fixed before the draw. A class whose adjacent shapes all come from one tracker is kept small, and a class with
# shapes from all three trackers is larger, so no parser's tracker supplies more than CAP of the outside adjacent records.
SIZE = {
    "urbanization": 2,
    "grid-wisconsin": 2,
    "grid-utah": 8,
    "spelled-number": 6,
    "intersection": 2,
    "highway-lettered": 8,
    "non-address-nightmare": 6,
    "box-glued": 6,
    "fraction-form": 8,
    "lot-trailer-site": 12,
}
ROUND = 8
CAP = 1 / 3  # no parser's own tracker supplies more than this share of the outside `adjacent` records
DEFAULT_PRIVATE = Path.home() / "projects/temp-postal/doorplate"
GOLD_REAL = ROOT / "local-data/golden-real"
BEGIN, END = "<!-- round-8 begin -->", "<!-- round-8 end -->"

SPELLED = ["One", "Two", "Three", "Four", "Five", "Six", "Eight", "Ten", "Twelve", "Twenty"]
ORDS = ["Twelfth", "Third", "Fifth", "Ninth", "Fourteenth", "Twentieth"]
COMPASS = [("North", "N"), ("South", "S"), ("East", "E"), ("West", "W")]
PAIRS = ["NE", "NW", "SE", "SW"]
PLACEHOLDERS = ["No Address On File", "Address Unknown", "None Given", "Not Provided", "Address Withheld"]
BOILER = ["Subject To Lien Held By Its Assigns", "Per Notice Of Record To Its Successors", "On Behalf Of Its Assignees"]
FOREIGN = [
    ("London", "SW{a}A {b}{c}{d}", "United Kingdom"),
    ("Toronto", "M{a}{c} {b}{d}{c}", "Canada"),
    ("Dublin", "D0{a} {c}{d}{b}{c}", "Ireland"),
]
# GeoNames' US file has no Puerto Rico rows: a few real (city, state, ZIP) triples stand in.
PR_PLACES = [
    ("San Juan", "PR", "00901"),
    ("Ponce", "PR", "00716"),
    ("Mayaguez", "PR", "00680"),
    ("Bayamon", "PR", "00956"),
    ("Caguas", "PR", "00725"),
    ("Carolina", "PR", "00979"),
    ("Arecibo", "PR", "00612"),
    ("Guaynabo", "PR", "00969"),
]
MIL_ZIP = {"AE": (90, 98), "AA": (34, 34), "AP": (962, 966)}


class G:
    """Helpers for one draw: the generator and the real places."""

    def __init__(self, r: random.Random, places):
        self.r = r
        self.places = places
        self.zero = [p for p in places if p[2].startswith("0")]
        self.pr = PR_PLACES
        self.tx = [p for p in places if p[1] == "TX"]

    def name(self):
        return templates.name(self.r)

    def num(self, lo=1, hi=9999):
        return self.r.randint(lo, hi)

    def typ(self):
        full, short = self.r.choice(templates.TYPES)
        return self.r.choice([full, short])

    def letter(self, chars="ABCDEFGH"):
        return self.r.choice(chars)

    def direction(self):
        full, short = self.r.choice(COMPASS)
        return self.r.choice([full, short])

    def ordinal(self):
        return templates.ordinal(self.r.randint(2, 99))

    def unit(self):
        return templates.unit(self.r, self.r.random() < 0.6)

    def spelled(self):
        return self.r.choice(SPELLED)

    def dddd(self):
        return f"{self.r.randint(1000, 9999)}"


def last(g: G, place) -> str:
    return templates.last_line(g.r, place, "full")


# A form is (tracker, builder); a builder returns (line 1, place list to draw from or None, last-line override or None).
def L1(f):
    return lambda g: (f(g), None, None)


def _zip_cut(kind):
    def build(g):
        place = g.r.choice(g.zero if kind == "zero" else g.places)
        city, st, z5 = place
        line1 = f"{g.num(1, 9999)} {g.name()} {g.typ()}"
        tail = {
            "hyphen": f"{z5}-{g.r.randint(1, 99):02d}",
            "nohyphen": f"{z5}{g.r.randint(10, 99)}",
            "space": f"{z5} {g.dddd()}",
            "zero": f"{z5[1:]} -{g.dddd()}",
            "zip-first": None,
        }[kind]
        if kind == "zip-first":
            return line1, None, f"{city} {z5}-{g.dddd()} {st}"
        return line1, None, f"{city}, {st} {tail}"

    return build


def _military(kind):
    def build(g):
        k, b = g.num(1, 9999), g.num(1, 999)
        st = g.r.choice(["AE", "AP", "AA"])
        lo, hi = MIL_ZIP[st]
        z = f"{g.r.randint(lo, hi):03d}{g.r.randint(0, 99):02d}"[:5] if st != "AA" else f"340{g.r.randint(0, 99):02d}"
        if st == "AE":
            z = f"09{g.r.randint(0, 99):03d}"[:5]
        elif st == "AP":
            z = f"{g.r.randint(962, 966)}{g.r.randint(0, 99):02d}"
        form = {
            "psc": f"PSC {k} Box {b}",
            "unit": f"Unit {k} Box {b}",
            "cmr": f"CMR {k} Box {b}",
            "ship": f"USS {g.name()} (DDG {g.num(1, 99)})",
            "dpo": f"Unit {k} Box {b}",
            "embassy": f"American Embassy {g.name()}, Unit {k} Box {b}",
        }[kind]
        city = {"psc": "APO", "unit": "APO", "cmr": "APO", "ship": "FPO", "dpo": "DPO", "embassy": "DPO"}[kind]
        return form, None, f"{city} {st} {z}"

    return build


def _pr(kind):
    def build(g):
        city, st, z5 = g.r.choice(g.pr)
        n, urb, st2 = g.num(1, 999), g.name(), g.name()
        line = {
            "urb-first": f"URB {urb}, {n} Calle {st2}",
            "urb-first2": f"URB {urb} {g.letter()}{g.num(1, 40)}, Calle {st2} {n}",
            "urb-after": f"{n} Calle {st2} URB {urb}",
            "street-first": f"Calle {st2} {n} {g.num(1, 9)}{g.letter()}",
            "calle-grid": f"Calle {g.num(1, 99)} #{g.num(1, 99)}-{g.num(1, 99)}",
        }[kind]
        return line, None, f"{city}, PR {z5}"

    return build


def _tx_private():
    def build(g):
        city, st, z5 = g.r.choice(g.tx)
        return f"{g.num(1, 9999)} PR {g.num(100, 999)}", None, f"{city}, TX {z5}"

    return build


def _intl(g):
    city, post, country = g.r.choice(FOREIGN)
    p = post.format(a=g.r.randint(1, 9), b=g.r.randint(1, 9), c=g.letter("ABCDEFGH"), d=g.r.randint(1, 9))
    return f"{g.num(1, 99)} {g.name()} Road", None, f"{city} {p}, {country}"


def _box_elder(g):
    city, st, z5 = g.r.choice(g.places)
    return f"PO Box {g.num(1, 999)}", None, f"Box {g.name()}, {st} {z5}"


def _inmate(g):
    city, st, z5 = g.r.choice(g.places)
    return (
        f"{g.r.choice(templates.PEOPLE)} {g.name()}, FRDC {g.num(1, 9999)} Route {g.letter()}, DOC #{g.num(100000, 999999)}",
        None,
        f"{city}, {st} {z5}",
    )


def _nan_city(g):
    city, st, z5 = g.r.choice(g.places)
    return f"{g.num()} {g.name()} {g.typ()}", None, f"{g.r.choice(['NaN', 'NULL', 'undefined', 'None'])}, {st} {z5}"


def _ssn(g):
    city, st, z5 = g.r.choice(g.places)
    name = f"{g.r.choice(templates.PEOPLE)} {g.name()}"
    return f"{name} {g.num(100, 999)}-{g.num(10, 99)}-{g.num(1000, 9999)}", None, f"{city}, {st} {z5}"


def _placeholder(g):
    city, st, z5 = g.r.choice(g.places)
    return g.r.choice(PLACEHOLDERS), None, f"{city}, {st} {z5}"


def _boiler(g):
    return f"{g.r.choice(BOILER)} {g.num()} {g.name()} {g.typ()}", None, None


def _line2(f1, f2):
    """Line 1 and a line 2 segment: `f1, f2, city, ST zip`."""
    return lambda g: (f"{f1(g)}, {f2(g)}", None, None)


FORMS: dict[str, dict[str, list[tuple[str, callable]]]] = {
    "second-number": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(10, 99)} {g.num(100, 999)} {g.name()} {g.typ()}")),
            (
                "D",
                L1(lambda g: (lambda a: f"{a} {a + 2 * g.num(1, 9)} {g.name()} {g.typ()}")(g.num(1000, 9990) // 2 * 2)),
            ),
        ],
        "adjacent": [
            (
                "D",
                L1(lambda g: (lambda a: f"{a} & {a + 2} {g.direction()} {g.ordinal()} {g.typ()}")(g.num(1, 90) | 1)),
            ),
            ("L", L1(lambda g: (lambda a: f"{a}&{a + 2} {g.name()} {g.typ()}")(g.num(2, 90) // 2 * 2))),
            ("D", L1(lambda g: (lambda a: f"{a},{a + 2} {g.name()} {g.typ()}")(g.num(1000, 9990) // 2 * 2))),
            ("L", L1(lambda g: (lambda a: f"{a}-{a + 2} {g.name()} {g.typ()}")(g.num(100, 990) // 2 * 2))),
        ],
    },
    "letter-before-street": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(1, 999)} {g.letter('ABCD')} {g.name()} {g.typ()}")),
            ("D", L1(lambda g: f"{g.num(1, 999)} {g.letter('ABCD')} {g.ordinal()} {g.typ()}")),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.num(1000, 99999)} {g.letter('JKMRT')} {g.letter('NSEW')} {g.name()} Blvd")),
            ("D", L1(lambda g: f"{g.letter('GHJKT')} {g.num(100, 9999)} {g.name()} {g.typ()}")),
            ("U", L1(lambda g: f"{g.num(100, 999)} {g.name()} {g.letter('JKMRTW')}. {g.name()} Hwy")),
        ],
    },
    "no-so-direction": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(100, 999)} NO {g.name()} {g.typ()}")),
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.typ()} SO")),
            ("D", L1(lambda g: f"{g.num(100, 999)} E {g.num(100, 9999)} SO")),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.name()} Co Rd SO")),
            ("L", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.r.choice(['Ci', 'Ct', 'Cir'])} {g.letter('NSEW')}")),
            ("U", L1(lambda g: f"{g.num(100, 999)} South St {g.letter('EW')}")),
            (
                "U",
                L1(lambda g: f"{g.num(100, 999)} {g.r.choice(['North', 'East', 'West'])} {g.typ()} {g.letter('NSEW')}"),
            ),
        ],
    },
    "county-road-compass": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(100, 9999)} County Road {g.r.choice(PAIRS)} {g.num(100, 9999)}")),
            (
                "D",
                L1(
                    lambda g: (
                        f"{g.num(10, 999)} {g.r.choice(['East', 'West', 'North'])} {g.r.choice(['KY', 'TR'])} {g.num(1, 99)}"
                    )
                ),
            ),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.num(100, 9999)} {g.name()} Road {g.num(1, 999)}")),
            ("U", L1(lambda g: f"{g.num(100, 9999)} Farm Road {g.num(100, 9999)}")),
            ("U", L1(lambda g: f"{g.num(1000, 9999)} S {g.r.choice(['East', 'West'])} Loop {g.num(100, 999)}")),
            ("U", L1(lambda g: f"{g.num(10000, 99999)} {g.r.choice(['RM', 'FM'])} {g.num(100, 9999)}")),
        ],
    },
    "zip4-cut": {
        "covered": [("D", _zip_cut("hyphen")), ("D", _zip_cut("nohyphen"))],
        "adjacent": [("D", _zip_cut("space")), ("D", _zip_cut("zero")), ("L", _zip_cut("zip-first"))],
    },
    "unit-before-street": {
        "covered": [
            (
                "D",
                L1(
                    lambda g: (
                        f"{g.num(1, 99)}-{g.num(10, 99)} {g.r.choice(['Suite', 'Ste', 'Apt'])} {g.num(1, 40)} {g.name()} {g.typ()}"
                    )
                ),
            ),
            (
                "D",
                L1(
                    lambda g: (
                        f"{g.r.choice(['Apt', 'Unit', 'Ste'])} {g.num(1, 40)}{g.letter('ABC')} {g.num(10, 999)} {g.name()} {g.typ()}"
                    )
                ),
            ),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.r.choice(['Apt', 'Rm'])} {g.letter()} {g.name()}")),
            ("D", L1(lambda g: (lambda x: f"{g.num(100, 999)} Apt {x} {g.name()} Dr, # {x}")(g.letter()))),
            ("U", L1(lambda g: f"{g.num(10, 999)} {g.r.choice(['Ste', 'Apt'])} {g.num(1, 40)} {g.name()}")),
            ("L", L1(lambda g: f"{g.num(100, 9999)} {g.name()} {g.typ()} #{g.letter('HJ')}{g.num(100, 999)}")),
        ],
    },
    "paren-unit": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.typ()} (Unit {g.num(1, 40)})")),
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.typ()} ({g.ordinal()} Fl)")),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.typ()} (Rear Entrance)")),
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()}({g.r.choice(['St', 'Ave', 'Dr'])})")),
            ("D", L1(lambda g: f"{g.num(10, 999)} {g.name()} ({g.name()} {g.typ()}")),
            ("L", L1(lambda g: f"{g.num(100, 999)} {g.letter('NSEW')}. {g.name()} St, {g.ordinal()} Floor")),
        ],
    },
    "military": {
        "covered": [
            ("P", _military("psc")),
            ("P", _military("unit")),
            ("P", _military("cmr")),
            ("P", _military("ship")),
        ],
        "adjacent": [("P", _military("dpo")), ("P", _military("embassy"))],
    },
    "urbanization": {
        "covered": [("P", _pr("urb-first")), ("P", _pr("urb-first2"))],
        "adjacent": [
            ("D", _pr("urb-after")),
            ("D", _pr("street-first")),
            ("D", _tx_private()),
            ("L", _pr("calle-grid")),
        ],
    },
    "grid-utah": {
        "covered": [
            ("P", L1(lambda g: f"{g.num(1, 999)} {g.letter('NSEW')} {g.num(1, 9) * 100} {g.letter('NSEW')}")),
            ("D", L1(lambda g: f"{g.num(100, 999)} E {g.num(100, 9999)} SO")),
        ],
        "adjacent": [
            (
                "U",
                L1(
                    lambda g: f"{g.num(10, 99) * 10} {g.letter('NSEW')} {g.num(1000, 6000) // 5 * 5} {g.letter('NSEW')}"
                ),
            ),
            (
                "L",
                L1(
                    lambda g: (
                        f"{g.num(10, 999)} {g.letter('NSEW')} {g.num(1, 9) * 100} {g.letter('NSEW')} #{g.num(1, 40)}"
                    )
                ),
            ),
        ],
    },
    "grid-wisconsin": {
        "covered": [
            (
                "U",
                L1(
                    lambda g: (
                        f"{g.letter('NSEW')}{g.num(1, 999)} {g.letter('NSEW')}{g.num(1000, 9999)} {g.name()} {g.typ()}"
                    )
                ),
            ),
        ],
        "adjacent": [
            (
                "D",
                L1(
                    lambda g: (
                        f"{g.letter('NSEW')}{g.num(1, 99)}{g.letter('NSEW')}{g.num(1000, 9999)} {g.name()} {g.typ()}"
                    )
                ),
            ),
            (
                "D",
                L1(
                    lambda g: (
                        f"{g.letter('NSEW')}{g.num(1, 99)} {g.letter('NSEW')}{g.num(1000, 9999)} {g.name()} {g.typ()} {g.unit()}"
                    )
                ),
            ),
        ],
    },
    "spelled-number": {
        "covered": [
            ("D", L1(lambda g: f"{g.spelled()} {g.name()} Park {g.r.choice(['Ave', 'Avenue', 'Dr'])}")),
            ("D", L1(lambda g: f"{g.spelled()} {g.name()} Plaza")),
        ],
        "adjacent": [
            ("D", _line2(lambda g: f"{g.num(100, 999)} {g.name()} {g.typ()}", lambda g: g.spelled())),
            ("D", L1(lambda g: f"{g.spelled()}, {g.name()} {g.typ()}")),
            ("U", L1(lambda g: f"{g.num(10, 999)} {g.letter('NSEW')} {g.r.choice(ORDS)} {g.typ()}")),
            ("U", L1(lambda g: f"{g.num(10, 999)} {g.spelled()} {g.typ()}")),
        ],
    },
    "intersection": {
        "covered": [
            ("U", L1(lambda g: f"{g.num(100, 9999)} {g.name()} & {g.name()} {g.r.choice(['Cmns', 'Plaza', 'Park'])}")),
            ("L", L1(lambda g: f"{g.num(10, 999)} {g.name()} & {g.name()} {g.typ()}")),
        ],
        "adjacent": [
            ("U", L1(lambda g: f"{g.name()} {g.typ()} / {g.name()} {g.typ()}")),
            ("U", L1(lambda g: f"{g.name()} {g.typ()} & {g.ordinal()} {g.typ()}")),
            ("U", L1(lambda g: f"{g.name()} Bldg {g.letter()}, {g.name()} {g.typ()} and {g.name()} {g.typ()}")),
        ],
    },
    "highway-lettered": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(10, 9999)} United States Highway {g.num(1, 99)}")),
            ("D", L1(lambda g: f"{g.num(10, 9999)} State Rd {g.letter('QRSTUVW') * 2}")),
            ("U", L1(lambda g: f"{g.num(10, 9999)} Business Route {g.num(1, 99)}")),
        ],
        "adjacent": [
            ("D", L1(lambda g: f"{g.num(10, 9999)} Old United States Highway {g.num(10, 49)}-{g.num(50, 99)}")),
            (
                "L",
                L1(lambda g: f"Lot {g.num(1, 20)}-{g.letter()} {g.r.choice(['MN', 'WI', 'OH'])} Hwy {g.num(100, 999)}"),
            ),
            ("U", L1(lambda g: f"{g.num(10, 9999)} US Hwy {g.num(1, 99)} & Hwy {g.num(100, 999)}")),
            ("L", L1(lambda g: f"{g.num(10, 9999)} State Route {g.num(1, 99)} #{g.num(100, 9999)}")),
            ("L", L1(lambda g: f"{g.num(10, 9999)} US Hwy {g.num(1, 99)} #{g.letter('HJ')}{g.num(100, 999)}")),
        ],
    },
    "non-address-nightmare": {
        "covered": [("D", _placeholder), ("D", _nan_city)],
        "adjacent": [("D", _boiler), ("D", _intl), ("U", _inmate), ("U", _ssn)],
    },
    "box-glued": {
        "covered": [
            ("D", L1(lambda g: f"Campus Box {g.num(1, 9999)}")),
            ("D", L1(lambda g: f"{g.name()} CPO #{g.num(1, 9999)}")),
            ("U", _box_elder),
        ],
        "adjacent": [
            (
                "D",
                L1(
                    lambda g: g.r.choice(
                        [
                            f"POBOX{g.num(1, 9999)}",
                            f"HCR{g.num(1, 99)} BOX {g.num(1, 99)}{g.letter()}",
                            f"P O BOX{g.num(1, 9999)}",
                        ]
                    )
                ),
            ),
            ("L", L1(lambda g: f"p.o.box {g.num(1, 99999)}")),
            ("L", L1(lambda g: f"P.O.Box{g.num(1, 99999)}")),
            ("D", L1(lambda g: g.r.choice([f"PO Drawer {g.letter()}", f"PO Box {g.r.choice(['NA', 'None', 'N/A'])}"]))),
        ],
    },
    "fraction-form": {
        "covered": [
            ("D", L1(lambda g: f"{g.num(10, 999)} 1 2 {g.name()} {g.typ()}")),
            ("D", L1(lambda g: f"{g.num(10, 999)} 1 2 {g.letter('NSEW')} {g.name()} {g.typ()}")),
        ],
        "adjacent": [
            (
                "L",
                L1(
                    lambda g: (
                        f"{g.num(10, 999)}{g.r.choice(['½', '¼', '¾'])} {g.letter('NSEW')} {g.ordinal()} {g.typ()}"
                    )
                ),
            ),
            ("U", L1(lambda g: f"{g.num(10, 9999)} 1/4 {g.name()} {g.typ()}")),
            ("L", L1(lambda g: f"{g.num(10, 999)}{g.r.choice(['½', '¼', '¾'])} {g.name()} {g.typ()}")),
        ],
    },
    "lot-trailer-site": {
        "covered": [
            ("U", L1(lambda g: f"Pier {g.num(1, 99)} Lot {g.num(1, 40)}")),
            ("U", L1(lambda g: f"{g.num(10, 999)} {g.name()} {g.typ()} Lot {g.num(1, 99)}")),
        ],
        "adjacent": [
            ("U", L1(lambda g: f"{g.num(100, 9999)} {g.ordinal()} Street Trailer {g.num(1, 99)}")),
            ("L", L1(lambda g: f"Lot {g.num(1, 20)}-{g.letter()} {g.r.choice(['MN', 'WI'])} {g.num(100, 999)}")),
            (
                "D",
                L1(
                    lambda g: g.r.choice(
                        [
                            f"{g.num(10, 99)} {g.name()} Fish Pier",
                            f"{g.num(1000, 9999)} {g.name()} {g.typ()} Msc {g.num(100, 999)}",
                        ]
                    )
                ),
            ),
        ],
    },
}


def issue_examples() -> set[str]:
    """Strings quoted (backticks) in the class table and the survey: none of them may be drawn."""
    out = set()
    for p in (ROOT / "tools/golden/tiers.py", ROOT / "docs/research/nightmare-survey.md"):
        for m in re.findall(r"`([^`]{8,})`", p.read_text(encoding="utf-8")):
            out.add(exclusions.norm(m))
    return out


def draw(seed: int, places, banned: set[str]):
    """The round: a list of dicts (text, shape, variant, tracker), shuffled; plus counts of rejected candidates."""
    nm = [c for c, v in CLASSES.items() if v.tier == "nightmare"]
    assert set(nm) == set(FORMS), set(nm) ^ set(FORMS)
    r = random.Random(seed)
    g = G(r, places)
    recs, seen, rejected = [], set(), collections.Counter()
    for cls in nm:
        for variant in ("covered", "adjacent"):
            forms = FORMS[cls][variant][:]
            r.shuffle(forms)
            got, tries = 0, 0
            while got < SIZE.get(cls, PER_CELL):
                tries += 1
                if tries > 500:
                    raise SystemExit(f"{cls}/{variant}: could not fill the cell")
                tracker, build = forms[got % len(forms)]
                line1, _, lastline = build(g)
                if lastline is None:
                    lastline = last(g, r.choice(places))
                text = f"{line1}, {lastline}"
                k = exclusions.norm(text)
                if k in seen:
                    rejected["duplicate"] += 1
                    continue
                if exclusions.hit(text, banned) or k in banned:
                    rejected["excluded"] += 1
                    continue
                seen.add(k)
                recs.append({"text": text, "shape": cls, "variant": variant, "tracker": tracker})
                got += 1
    r.shuffle(recs)
    return recs, rejected


def cap_report(recs):
    """Tracker shares of the outside `adjacent` records (D, U, L only; Pub 28 forms are not a parser's tracker)."""
    c = collections.Counter(
        x["tracker"] for x in recs if x["variant"] == "adjacent" and CLASSES[x["shape"]].origin == "outside"
    )
    total = sum(c[t] for t in "DUL")
    return {t: c[t] / total for t in "DUL"}, total


def lines(recs, tag):
    return [
        json.dumps({"id": f"{tag}-r{ROUND}-{i:03d}", "text": x["text"]}, ensure_ascii=False)
        for i, x in enumerate(recs, 1)
    ]


def prov_lines(recs, tag):
    return [
        json.dumps(
            {
                "id": f"{tag}-r{ROUND}-{i:03d}",
                "round": ROUND,
                "stratum": "template",
                "source": "template",
                "shape": x["shape"],
                "style": "none",
                "variant": x["variant"],
                "tracker": x["tracker"],
            },
            ensure_ascii=False,
        )
        for i, x in enumerate(recs, 1)
    ]


def manifest_block(recs, sha_round, sha_prov) -> str:
    byv = collections.Counter(x["variant"] for x in recs)
    byc = collections.Counter(x["shape"] for x in recs)
    shares, total = cap_report(recs)
    doorplate_side = sum(CLASSES[x["shape"]].origin == "doorplate-research" for x in recs)
    return f"""{BEGIN}
## Round 8 (`nightmare`, issue #22)

Seed {PUBLIC_SEED}, drawn by `tools/golden/nightmare.py`: {len(recs)} unlabeled records, (class, variant) cells of {PER_CELL} unless `SIZE` says otherwise
for {len(byc)} paired classes (cell sizes in `SIZE`, equal for the two variants of a class). Every string is invented; city, state and ZIP are real. The variant is set by the form that
wrote the string, never by a parser run (`COMPOSITION.md`, "`nightmare` classes are paired").

- `round-8.jsonl`: `{sha_round}`
- `provenance.jsonl` (all rounds, with `variant` and `tracker` on round 8): `{sha_prov}`

| Share | Records |
|---|---|
| covered | {byv["covered"]} |
| adjacent | {byv["adjacent"]} |
| doorplate-research classes | {doorplate_side} ({doorplate_side / len(recs):.0%}) |
| outside classes | {len(recs) - doorplate_side} ({1 - doorplate_side / len(recs):.0%}) |

Outside `adjacent` records by the tracker the shape came from (cap one third each; Pub 28 forms excluded, {total} records):
doorplate {shares["D"]:.0%}, usaddress {shares["U"]:.0%}, libpostal {shares["L"]:.0%}.

| Class | Records |
|---|---|
{chr(10).join(f"| {k} | {v} |" for k, v in sorted(byc.items()))}
{END}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--twin", action="store_true", help="the private twin: unpublished seed, doorplate's local-data")
    ap.add_argument(
        "--check", action="store_true", help="redraw with the public seed and compare with what is committed"
    )
    ap.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    a = ap.parse_args()
    root = a.private_root

    from tools.golden import sample  # reads the same exclusion corpora as rounds 1 to 6

    banned, counts = sample.exclusion_set(root)
    banned = banned | issue_examples()
    for p in (ROOT / "sets/golden/rounds").glob("round-[1-6].jsonl"):  # no repeat of a public record
        banned |= {exclusions.norm(json.loads(x)["text"]) for x in p.read_text().splitlines()}
    places = templates.read_places(root / "local-data/places/geonames-postal/us/US.txt")

    if a.twin:
        tdir = root / "local-data/golden-twin"
        seed_file = tdir / "SEED-r8"
        if seed_file.exists():
            seed = int(seed_file.read_text())
        elif a.confirm:
            seed = secrets.randbelow(10**9) + 10**9
            seed_file.write_text(str(seed))
        else:
            seed = 0
        out, tag = tdir, "t"
        banned |= (
            {  # the twin never repeats a public round-8 record either
                exclusions.norm(json.loads(x)["text"])
                for x in (ROOT / "sets/golden/rounds/round-8.jsonl").read_text().splitlines()
            }
            if (ROOT / "sets/golden/rounds/round-8.jsonl").exists()
            else set()
        )
    else:
        seed, out, tag = PUBLIC_SEED, ROOT / "sets/golden", "g"
    recs, rejected = draw(seed, places, banned)
    shares, total = cap_report(recs)
    print(
        f"{len(recs)} records; rejected {dict(rejected)}; exclusion set {len(banned):,} strings from {len(counts)} places"
    )
    print("outside adjacent tracker shares:", {k: f"{v:.0%}" for k, v in shares.items()}, "of", total)
    over = {k: v for k, v in shares.items() if v > CAP + 1e-9}
    if (
        over and a.twin
    ):  # forms are dealt in seeded order, so shares move a little with the seed; the public draw is held to the cap
        print(f"note: twin shares differ from the cap of one third: {over}")
    elif over:
        raise SystemExit(f"cap of one third exceeded: {over}")

    body = "\n".join(lines(recs, tag)) + "\n"
    if a.check:
        p = out / "rounds" / f"round-{ROUND}.jsonl"
        ok = p.exists() and p.read_text(encoding="utf-8") == body
        print("matches the committed round" if ok else "DIFFERS from the committed round")
        raise SystemExit(0 if ok else 1)
    if not a.confirm:
        print("(dry run: pass --confirm to write)")
        return
    (out / "rounds").mkdir(parents=True, exist_ok=True)
    rp = out / "rounds" / f"round-{ROUND}.jsonl"
    rp.write_text(body, encoding="utf-8")
    pl = prov_lines(recs, tag)
    if a.twin:
        (out / "provenance-r8.jsonl").write_text("\n".join(pl) + "\n", encoding="utf-8")
        real = out / "real" / "rounds"
        real.mkdir(parents=True, exist_ok=True)
        (real / f"round-{ROUND}.jsonl").write_text(body, encoding="utf-8")  # invented text: real == shipped
        print(f"wrote the twin round to {out}")
        return
    pp = out / "provenance.jsonl"
    kept = [x for x in pp.read_text().splitlines() if x.strip() and json.loads(x)["round"] != ROUND]
    pp.write_text("\n".join(kept + pl) + "\n", encoding="utf-8")
    (GOLD_REAL / "rounds").mkdir(parents=True, exist_ok=True)
    (GOLD_REAL / "rounds" / f"round-{ROUND}.jsonl").write_text(body, encoding="utf-8")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    mp = out / "MANIFEST.md"
    md = mp.read_text(encoding="utf-8")
    md = re.sub(rf"\n?{re.escape(BEGIN)}.*?{re.escape(END)}\n?", "", md, flags=re.S)
    mp.write_text(md.rstrip("\n") + "\n\n" + manifest_block(recs, sha(rp), sha(pp)), encoding="utf-8")
    print(f"wrote {rp} and appended {len(pl)} provenance rows; manifest section updated")


if __name__ == "__main__":
    main()
