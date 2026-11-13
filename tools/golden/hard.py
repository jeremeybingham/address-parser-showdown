#!/usr/bin/env python3
"""Draw round 7 (`hard`, added): rarer shapes and observed typo classes on invented values.

    uv run python -m tools.golden.hard             # the plan and a dry draw with the exclusion check
    uv run python -m tools.golden.hard --confirm   # writes sets/golden/rounds/round-7.jsonl (public seed)
    uv run python -m tools.golden.hard --confirm --twin   # the private twin (unpublished seed), doorplate's local-data
    uv run python -m tools.golden.hard --check     # redraw and compare with the committed round

Round 7 is not paired (COMPOSITION.md): its classes are not derived from doorplate's rules. Each class in `SIZE` is a
shape in `tools/golden/tiers.py` with tier `hard`; the seven classes added for this round get 30 records each (20 for the
non-addresses), and nine base `hard` classes get 11 each, 299 in all. The class and the weights are fixed here, before
labeling; no parser is run. Only the (city, state, ZIP) triples are real (GeoNames). Rounds 1 to 6 and 8 are never touched.
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

PUBLIC_SEED = 20261114
ROUND = 7
SIZE = {
    "typo-glued": 30,
    "typo-type": 30,
    "zip4-plain": 30,
    "state-spelled": 30,
    "two-units": 30,
    "pre-type": 30,
    "non-address-hard": 20,
    "fraction": 11,
    "hyphen-number": 11,
    "rural-route": 11,
    "care-of": 11,
    "general-delivery": 11,
    "typo": 11,
    "box-and-street": 11,
    "named-place": 11,
    "no-street": 11,
}
DEFAULT_PRIVATE = Path.home() / "projects/temp-postal/doorplate"
GOLD_REAL = ROOT / "local-data/golden-real"
BEGIN, END = "<!-- round-7 begin -->", "<!-- round-7 end -->"

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
    "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}  # fmt: skip
TYPE_SLIPS = {
    "Street": ["Stret", "Streeet", "Sreet", "Steet"],
    "Avenue": ["Avnue", "Aveneu", "Avenuee", "Aveue"],
    "Road": ["Raod", "Roda", "Rooad", "Rd."],
    "Drive": ["Drvie", "Driev", "Drivee", "Dirve"],
    "Lane": ["Lnae", "Laen", "Lanee", "Lan"],
    "Court": ["Cuort", "Courtt", "Crt", "Coutr"],
    "Boulevard": ["Boulavard", "Bouelvard", "Boulevrd", "Blvrd"],
    "Circle": ["Cirlce", "Circel", "Circlee", "Crcle"],
    "Place": ["Plaec", "Placee", "Palce", "Plce"],
    "Trail": ["Trial", "Triail", "Trall", "Traill"],
    "Terrace": ["Terrase", "Terace", "Terracee", "Teraace"],
}
UNIT_SLIPS = [("Apt", "Aptt"), ("Apt", "Atp"), ("Suite", "Sutie"), ("Suite", "Siute"), ("Unit", "Unti"), ("Unit", "Uint"),
              ("Ste", "Stee"), ("Bldg", "Bldng"), ("Floor", "Flor")]  # fmt: skip
PLACEHOLDERS = ["Same As Above", "See Attached", "Unknown", "Deceased", "Homeless", "Return To Sender", "No Mail Accepted",
                "Not Applicable", "Refused", "To Be Determined", "Address Pending", "Moved Left No Forwarding"]  # fmt: skip
PRE_TYPES = ["Avenue", "Calle", "Camino", "Via", "Rue", "Route", "Highway", "Boulevard", "Paseo", "Vista"]
BUILDINGS = ["Tower", "Plaza", "Center", "Hall", "Annex", "Pavilion", "Commons"]
UNIT_PAIRS = [("Bldg", "Apt"), ("Building", "Suite"), ("Ste", "Rm"), ("Apt", "Fl"), ("Unit", "Rm"), ("Bldg", "Unit"),
              ("Fl", "Ste"), ("Apt", "Bldg")]  # fmt: skip


def last(r, place, form="full"):
    return templates.last_line(r, place, form)


def abbr(r):
    return r.random() < 0.6


def _glued(g, places):
    r = g
    place = r.choice(places)
    city, st, z5 = place
    kind = r.choice(["name-type", "city-state", "number-name", "city-zip"])
    full, short = r.choice(templates.TYPES)
    t = short if abbr(r) else full
    n = templates.number(r)
    nm = templates.name(r)
    if kind == "name-type":
        return f"{n} {nm}{t}, {city}, {st} {z5}"
    if kind == "city-state":
        return f"{n} {nm} {t}, {city},{st} {z5}"
    if kind == "number-name":
        return f"{n}{nm} {t}, {city}, {st} {z5}"
    return f"{n} {nm} {t}, {city}, {st}{z5}"


def _type_slip(r, places):
    place = r.choice(places)
    n, nm = templates.number(r), templates.name(r)
    if r.random() < 0.6:
        full = r.choice(list(TYPE_SLIPS))
        slip = r.choice(TYPE_SLIPS[full])
        line = f"{n} {nm} {slip}"
        if r.random() < 0.3:
            line += " " + templates.unit(r, True)
    else:
        word, slip = r.choice(UNIT_SLIPS)
        full, short = r.choice(templates.TYPES)
        line = f"{n} {nm} {short} {slip} {r.randint(1, 40)}"
    return f"{line}, {last(r, place)}"


def _zip4_plain(r, places):
    city, st, z5 = r.choice(places)
    full, short = r.choice(templates.TYPES)
    line = f"{templates.number(r)} {templates.name(r)} {short if abbr(r) else full}"
    if r.random() < 0.25:
        line += " " + templates.unit(r, True)
    return f"{line}, {city}, {st} {z5}{r.randint(1000, 9999)}"


def _state_spelled(r, places):
    city, st, z5 = r.choice(places)
    line = f"{templates.number(r)} {templates.street_core(r, abbr(r))}"
    name = STATES[st]
    if r.random() < 0.3:
        return f"{line}, {city}, {name}"
    return f"{line}, {city}, {name} {z5}"


def _two_units(r, places):
    place = r.choice(places)
    a, b = r.choice(UNIT_PAIRS)
    line = f"{templates.number(r)} {templates.street_core(r, True)}"
    ua, ub = r.randint(1, 20), r.choice([str(r.randint(1, 40)), r.choice("ABCDEF")])
    mid = r.choice([", ", " "])
    return f"{line} {a} {ua}{mid}{b} {ub}, {last(r, place)}"


def _pre_type(r, places):
    place = r.choice(places)
    t = r.choice(PRE_TYPES)
    tail = r.choice([r.choice("ABCDEFGH"), str(r.randint(1, 99)), templates.name(r)])
    return f"{templates.number(r)} {t} {tail}, {last(r, place)}"


def _non_address(r, places):
    city, st, z5 = r.choice(places)
    kind = r.choice(["alone", "city", "full"])
    word = r.choice(PLACEHOLDERS)
    if kind == "alone":
        return word
    if kind == "city":
        return f"{word}, {city}, {st}"
    return f"{word}, {city}, {st} {z5}"


def _std(shape):
    """A base `hard` shape from templates.py (the shape's own builder; no modifier but case)."""

    def build(r, places):
        for s in templates.SHAPES:
            if s[0] == shape:
                line = s[2](r, abbr(r))
                return f"{line}, {last(r, r.choice(places))}"
        raise KeyError(shape)

    return build


def _typo(r, places):
    text = _std(r.choice(["street-plain", "street-unit", "directional", "highway"]))(r, places)
    out = templates.typo(r, text)
    return out if out != text else templates.typo(r, text)


def _box_street(r, places):
    place = r.choice(places)
    box = templates._po_box(r, True)
    street = f"{templates.number(r)} {templates.street_core(r, True)}"
    a, b = (box, street) if r.random() < 0.5 else (street, box)
    return f"{a}, {b}, {last(r, place)}"


def _named_place(r, places):
    place = r.choice(places)
    kind = r.choice(["building", "person", "dept"])
    street = f"{templates.number(r)} {templates.street_core(r, True)}"
    if kind == "building":
        return f"{templates.name(r)} {r.choice(BUILDINGS)}, {street}, {last(r, place)}"
    if kind == "person":
        return f"{r.choice(templates.PEOPLE)} {templates.name(r)}, {street}, {last(r, place)}"
    return f"{r.choice(['Attn', 'Dept', 'Office of'])} {templates.name(r)}, {street}, {last(r, place)}"


def _no_street(r, places):
    city, st, z5 = r.choice(places)
    kind = r.choice(["city-state", "city-zip", "stray"])
    if kind == "city-state":
        return f"{city}, {st}"
    if kind == "city-zip":
        return f"{city}, {st} {z5}"
    return f"{templates.name(r)}, {city}, {st}"


BUILDERS = {
    "typo-glued": _glued,
    "typo-type": _type_slip,
    "zip4-plain": _zip4_plain,
    "state-spelled": _state_spelled,
    "two-units": _two_units,
    "pre-type": _pre_type,
    "non-address-hard": _non_address,
    "fraction": _std("fraction"),
    "hyphen-number": _std("hyphen-number"),
    "rural-route": _std("rural-route"),
    "care-of": _std("care-of"),
    "general-delivery": _std("general-delivery"),
    "typo": _typo,
    "box-and-street": _box_street,
    "named-place": _named_place,
    "no-street": _no_street,
}
STYLES = [("none", 78), ("upper", 12), ("lower", 4), ("nocomma", 6)]


def style(r, cls):
    names = [s for s in STYLES if not (cls in ("typo-glued", "non-address-hard") and s[0] == "nocomma")]
    return r.choices([s[0] for s in names], weights=[s[1] for s in names])[0]


def apply(text, st):
    return {
        "none": text,
        "upper": text.upper(),
        "lower": text.lower(),
        "nocomma": text.replace(",", ""),
    }[st]


def issue_examples() -> set[str]:
    out = set()
    p = ROOT / "tools/golden/tiers.py"
    for m in re.findall(r"`([^`]{8,})`", p.read_text(encoding="utf-8")):
        out.add(exclusions.norm(m))
    return out


def draw(seed: int, places, banned: set[str]):
    assert set(SIZE) == {c for c, v in CLASSES.items() if v.tier == "hard" and c in BUILDERS}, "classes and SIZE differ"
    r = random.Random(seed)
    recs, seen, rejected = [], set(), collections.Counter()
    for cls, n in SIZE.items():
        got, tries = 0, 0
        while got < n:
            tries += 1
            if tries > 2000:
                raise SystemExit(f"{cls}: could not fill the class")
            st = style(r, cls)
            text = apply(BUILDERS[cls](r, places), st)
            k = exclusions.norm(text)
            if k in seen:
                rejected["duplicate"] += 1
                continue
            if exclusions.hit(text, banned) or k in banned:
                rejected["excluded"] += 1
                continue
            seen.add(k)
            recs.append({"text": text, "shape": cls, "style": st})
            got += 1
    r.shuffle(recs)
    return recs, rejected


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
                "style": x["style"],
            },
            ensure_ascii=False,
        )
        for i, x in enumerate(recs, 1)
    ]


def manifest_block(recs, sha_round, sha_prov) -> str:
    byc = collections.Counter(x["shape"] for x in recs)
    return f"""{BEGIN}
## Round 7 (`hard`, added)

Seed {PUBLIC_SEED}, drawn by `tools/golden/hard.py`: {len(recs)} unlabeled records in {len(byc)} `hard` classes (sizes in `SIZE`: 30 for each
of the six added shape classes, 20 for the non-addresses, 11 for each of nine base `hard` classes). Every string is
invented; city, state and ZIP are real. The class is the shape the string was written from, never a parser run.

- `round-7.jsonl`: `{sha_round}`
- `provenance.jsonl` (all rounds): `{sha_prov}`

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

    from tools.golden import sample

    banned, counts = sample.exclusion_set(root)
    banned = banned | issue_examples()
    for p in (ROOT / "sets/golden/rounds").glob("round-*.jsonl"):
        if p.name != f"round-{ROUND}.jsonl":
            banned |= {exclusions.norm(json.loads(x)["text"]) for x in p.read_text().splitlines()}
    places = templates.read_places(root / "local-data/places/geonames-postal/us/US.txt")

    if a.twin:
        tdir = root / "local-data/golden-twin"
        seed_file = tdir / "SEED-r7"
        if seed_file.exists():
            seed = int(seed_file.read_text())
        elif a.confirm:
            seed = secrets.randbelow(10**9) + 10**9
            seed_file.write_text(str(seed))
        else:
            seed = 0
        out, tag = tdir, "t"
        pub = ROOT / "sets/golden/rounds/round-7.jsonl"
        if pub.exists():
            banned |= {exclusions.norm(json.loads(x)["text"]) for x in pub.read_text().splitlines()}
    else:
        seed, out, tag = PUBLIC_SEED, ROOT / "sets/golden", "g"
    recs, rejected = draw(seed, places, banned)
    print(
        f"{len(recs)} records; rejected {dict(rejected)}; exclusion set {len(banned):,} strings from {len(counts)} places"
    )

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
        (out / "provenance-r7.jsonl").write_text("\n".join(pl) + "\n", encoding="utf-8")
        real = out / "real" / "rounds"
        real.mkdir(parents=True, exist_ok=True)
        (real / f"round-{ROUND}.jsonl").write_text(body, encoding="utf-8")
        print(f"wrote the twin round to {out}")
        return
    pp = out / "provenance.jsonl"
    rows = [x for x in pp.read_text().splitlines() if x.strip() and json.loads(x)["round"] != ROUND]
    before = [x for x in rows if json.loads(x)["round"] < ROUND]
    after = [x for x in rows if json.loads(x)["round"] > ROUND]
    pp.write_text("\n".join(before + pl + after) + "\n", encoding="utf-8")
    (GOLD_REAL / "rounds").mkdir(parents=True, exist_ok=True)
    (GOLD_REAL / "rounds" / f"round-{ROUND}.jsonl").write_text(body, encoding="utf-8")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    mp = out / "MANIFEST.md"
    md = mp.read_text(encoding="utf-8")
    md = re.sub(rf"\n?{re.escape(BEGIN)}.*?{re.escape(END)}\n?", "", md, flags=re.S)
    block = manifest_block(recs, sha(rp), sha(pp))
    i = md.find("<!-- round-8 begin -->")
    md = md[:i] + block + "\n" + md[i:] if i >= 0 else md.rstrip("\n") + "\n\n" + block
    mp.write_text(md, encoding="utf-8")
    print(f"wrote {rp} and {len(pl)} provenance rows; manifest section updated")


if __name__ == "__main__":
    main()
