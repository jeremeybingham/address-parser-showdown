#!/usr/bin/env python3
"""Draw the golden set (#3, step 2): about 1,500 unlabeled records in rounds of 250.

    uv run python tools/golden/sample.py              # prints the plan and does nothing else
    uv run python tools/golden/sample.py --confirm    # writes sets/golden/ (the public set, seed in COMPOSITION.md)
    uv run python tools/golden/sample.py --confirm --twin   # the private twin, an unpublished seed, in doorplate's local-data
    uv run python tools/golden/sample.py --check      # re-runs the exclusion string check on the committed rounds
    uv run python tools/golden/sample.py --confirm --real   # the same draw unmasked, for labeling (local-data/golden-real/)

The composition is in `sets/golden/COMPOSITION.md` and the constants below; both are fixed before any labeling. Records are
drawn by a seeded hash (never by what a parser does with them), anonymized, checked against every exclusion corpus and
dealt into rounds so each round has the same mix. Maintainers only: it reads the private data in doorplate's
`local-data/`. It prints counts and shapes, never a record.

`--real` redoes the draw, checks that it reproduces the committed rounds byte for byte, and writes the same cards with
the row's own text (before anonymizing) to the git-ignored `local-data/golden-real/rounds/` (with `--twin`: the twin's
`real/rounds/`). Labeling is done on that text; `tools/golden/derive.py` makes the shipped text from the labels.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.metadata
import json
import random
import re
import secrets
import sys
from pathlib import Path

import doorplate
import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from tools.golden import exclusions, templates  # noqa: E402

PUBLIC_SEED = 20261112
TOTAL, ROUND_SIZE = 1500, 250
# stratum -> quota. `public` is split over its sources; `template` is hand templates; `clean` is ordinary NAD forms.
QUOTA = {"public": 600, "template": 600, "clean": 300}
PUBLIC_SOURCES = {  # source -> quota (sum = QUOTA["public"])
    "nad": 300,
    "fmcsa": 60,
    "tdlr": 60,
    "va-scc": 60,
    "ny-corps": 60,
    "fcc-amateur": 60,
}
OVERSAMPLE = 6  # candidates drawn per wanted record; the filters drop some
STYLES = [("mixed-commas", 40), ("upper-commas", 30), ("upper-nocommas", 20), ("mixed-nocommas", 10)]
STATES = set(
    [
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
    ]
)

DEFAULT_PRIVATE = Path.home() / "projects/temp-postal/doorplate"
REAL_DIR = ROOT / "local-data/golden-real"  # unmasked rounds and private gold (git-ignored)
SAFE = {  # words the anonymizer may keep (they decide how a line parses); anything else it keeps is a leak
    "street",
    "avenue",
    "road",
    "drive",
    "lane",
    "court",
    "boulevard",
    "circle",
    "way",
    "place",
    "trail",
    "terrace",
    "highway",
    "route",
    "county",
    "state",
    "box",
    "post",
    "office",
    "rural",
    "suite",
    "apartment",
    "building",
    "floor",
    "room",
    "unit",
    "lot",
    "trailer",
    "north",
    "south",
    "east",
    "west",
    "northeast",
    "northwest",
    "southeast",
    "southwest",
    "general",
    "delivery",
    "star",
    "frontage",
    "interstate",
    "parkway",
    "plaza",
    "square",
    "loop",
    "attn",
    "apt",
    "ste",
    "bldg",
    "hwy",
    "blvd",
    "pkwy",
    "trlr",
}
# private sources: name -> (parquet, street columns, city, state, zip)
MESSY = {
    "fmcsa": ("local-data/fmcsa-census-2026/records.parquet", ["line1", "line2"], "city", "state", "zip"),
    # TDLR has one `last_line` field ("CITY, ST 12345"); the three parts are cut out of it in SQL
    "tdlr": (
        "local-data/tx-tdlr-2026/records.parquet",
        ["line1", "line2"],
        "regexp_extract(last_line, '^(.*?),?\\s+([A-Za-z]{2})\\s+([0-9]{5})', 1)",
        "regexp_extract(last_line, '^(.*?),?\\s+([A-Za-z]{2})\\s+([0-9]{5})', 2)",
        "regexp_extract(last_line, '^(.*?),?\\s+([A-Za-z]{2})\\s+([0-9]{5})', 3)",
    ),
    "va-scc": ("local-data/va-scc-2026/records.parquet", ["line1", "line2"], "city", "state", "zip"),
    "ny-corps": ("local-data/ny-corps-2026/records.parquet", ["line1", "line2"], "city", "state", "zip"),
    "fcc-amateur": ("local-data/fcc-uls-amateur-2026/en_addr.parquet", ["street_address"], "city", "state", "zip_code"),
}
NAD = "local-data/nad-2026/nad_r24.parquet"
NAD_EXTRA = ["Unit", "Room", "Floor", "Building", "SubAddress"]
EXCLUSION_PATHS = [  # relative to the doorplate checkout, except libpostal
    "tests/corpus",
    "tests/external",
    "benchmarks/suite/v1",
    "local-data/benchsuite/usaddress-training",
    "local-data/geocode-benchmark",
]
LIBPOSTAL_TESTS = Path.home() / "projects/libpostal-senzing/src/test"


def weighted(r: random.Random, pairs):
    return r.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]


def style(r: random.Random, street: str, city: str, state: str, zip5: str, name: str | None = None) -> tuple[str, str]:
    name = name or weighted(r, STYLES)
    text = f"{street}, {city}, {state} {zip5}"
    if name.startswith("upper"):
        text = text.upper()
    if name.endswith("nocommas"):
        text = text.replace(",", "")
    return text, name


def top_by_hash(con, sql_from: str, where: str, key_cols: list[str], seed: int, k: int, cols: str):
    """The k rows with the smallest hash of (seed, row): a deterministic random sample, whatever the thread count."""
    key = " || '|' || ".join(f"coalesce(cast({c} as varchar), '')" for c in key_cols)
    q = f"select {cols} from {sql_from} where {where} order by hash({key} || '|{seed}') limit {k}"
    return con.execute(q).fetchall()


def leaked(original: str, anon: str) -> bool:
    keep = set(re.findall(r"[A-Za-z]{4,}", original.lower())) & set(re.findall(r"[A-Za-z]{4,}", anon.lower()))
    return bool(keep - SAFE)


def anonymize(streets: list[str], seed: int) -> list[str | None]:
    """Anonymized street lines; None where the anonymizer changed the parse (not faithful) or kept a real word."""
    res = doorplate.Anonymizer(seed=seed).anonymize_many(streets)
    return [x.text if x.faithful and not leaked(s, x.text) else None for s, x in zip(streets, res, strict=True)]


def draw_nad(con, root: Path, seed: int, k: int, clean: bool):
    where = (
        "State is not null and AddNo_Full is not null and StNam_Full is not null and Post_City is not null "
        "and regexp_matches(coalesce(Zip_Code, ''), '^[0-9]{5}')"
    )
    if clean:
        where += (
            " and regexp_matches(AddNo_Full, '^[0-9]+$') and coalesce(AddNum_Pre, '') = '' and coalesce(AddNum_Suf, '') = ''"
            " and coalesce(St_PreMod, '') = '' and coalesce(St_PosMod, '') = ''"
            + "".join(f" and coalesce({c}, '') = ''" for c in NAD_EXTRA)
        )
    cols = "State, AddNo_Full, StNam_Full, Post_City, Zip_Code, Unit, Room, Floor, Building, SubAddress"
    rows = top_by_hash(
        con,
        f"read_parquet('{root / NAD}')",
        where,
        ["State", "AddNo_Full", "StNam_Full", "Zip_Code", "Unit"],
        seed + (1 if clean else 0),
        k,
        cols,
    )
    out = []
    for st, num, name, city, zipc, unit, room, floor, bld, sub in rows:
        if st not in STATES:
            continue
        parts = [num, name] + [x for x in (bld, floor, unit, room, sub) if x]
        out.append((" ".join(p.strip() for p in parts if p.strip()), city.strip().title(), st, zipc[:5]))
    return out


def draw_messy(con, root: Path, source: str, seed: int, k: int):
    path, scols, ccol, stcol, zcol = MESSY[source]
    where = (
        f"{scols[0]} is not null and length(trim({scols[0]})) >= 5 and {ccol} is not null and upper({stcol}) in "
        f"({','.join(repr(s) for s in sorted(STATES))}) and regexp_matches(coalesce({zcol}, ''), '^[0-9]{{5}}')"
    )
    cols = ", ".join([f"coalesce({c}, '')" for c in scols] + [ccol, stcol, zcol])
    rows = top_by_hash(con, f"read_parquet('{root / path}')", where, scols + [ccol, stcol, zcol], seed, k, cols)
    out = []
    for r in rows:
        street = ", ".join(x.strip() for x in r[: len(scols)] if x.strip())
        out.append((street, r[-3].strip().title(), r[-2].upper(), r[-1][:5]))
    return out


def build(root: Path, seed: int, banned: set[str], skipped: list[dict] | None = None):
    """All records as dicts (text, stratum, source, shape, style), before rounds.

    `skipped`, if given, receives the rows the walk dropped as leak-or-unfaithful (round 9, `restore`)."""
    r = random.Random(seed)
    con = duckdb.connect()
    recs: list[dict] = []
    seen: set[str] = set()
    dropped = collections.Counter()

    def add(stratum, source, text, shape, sty, real=None):
        k = exclusions.norm(text)
        if k in seen:
            dropped[f"{source}:duplicate"] += 1
            return False
        if exclusions.hit(text, banned):
            dropped[f"{source}:excluded"] += 1
            return False
        seen.add(k)
        recs.append(
            {"text": text, "real": real or text, "stratum": stratum, "source": source, "shape": shape, "style": sty}
        )
        return True

    def take(stratum, source, rows, want, shape, force_style=None):
        streets = anonymize([x[0] for x in rows], seed)
        n = 0
        for (street, city, st, z), anon in zip(rows, streets, strict=True):
            if n >= want:
                break
            if anon is None:
                dropped[f"{source}:leak-or-unfaithful"] += 1
                if skipped is not None:
                    skipped.append(
                        {
                            "stratum": stratum,
                            "source": source,
                            "shape": shape,
                            "force": force_style,
                            "row": (street, city, st, z),
                        }
                    )
                continue
            text, sty = style(r, anon, city, st, z, force_style)
            real, _ = style(r, street, city, st, z, sty)  # a named style draws nothing from r: the draw is unchanged
            n += add(stratum, source, text, shape, sty, real)
        if n < want:
            raise SystemExit(f"{source}: only {n} of {want} records after filters; raise OVERSAMPLE")

    for source, want in PUBLIC_SOURCES.items():
        if source == "nad":
            rows = draw_nad(con, root, seed, want * OVERSAMPLE, clean=False)
        else:
            rows = draw_messy(con, root, source, seed, want * OVERSAMPLE)
        take("public", source, rows, want, "as-found")
    take(
        "clean",
        "nad",
        draw_nad(con, root, seed, QUOTA["clean"] * OVERSAMPLE, clean=True),
        QUOTA["clean"],
        "ordinary",
        "mixed-commas",
    )
    places = templates.read_places(root / "local-data/places/geonames-postal/us/US.txt")
    n = 0
    for text, shape, mod in templates.make(r, places, QUOTA["template"] * 3):
        if n >= QUOTA["template"]:
            break
        n += add("template", "template", text, shape, mod)
    return recs, dropped


def restore(skipped: list[dict], recs: list[dict], seed: int, banned: set[str]):
    """Round 9: the rows the walk dropped as leak-or-unfaithful, on their own text (no anonymizer call here).

    Own random generator, so rounds 1 to 6 are untouched. Duplicates (of a kept row's own text or of each other) and
    exclusion-corpus hits are dropped as before; they are not parser behavior. Returns (records, dropped counts)."""
    r = random.Random(seed + 9)
    seen = {exclusions.norm(x["real"]) for x in recs}
    out, dropped = [], collections.Counter()
    for x in skipped:
        street, city, st, z = x["row"]
        sty = x["force"] or weighted(r, STYLES)
        text, _ = style(r, street, city, st, z, sty)
        k = exclusions.norm(text)
        if k in seen:
            dropped[f"{x['source']}:duplicate"] += 1
        elif exclusions.hit(text, banned):
            dropped[f"{x['source']}:excluded"] += 1
        else:
            seen.add(k)
            out.append(
                {
                    "text": text,
                    "real": text,
                    "stratum": x["stratum"],
                    "source": x["source"],
                    "shape": x["shape"],
                    "style": sty,
                    "restored": True,
                }
            )
    r.shuffle(out)
    return out, dropped


def deal(recs: list[dict], seed: int) -> list[list[dict]]:
    """Rounds of ROUND_SIZE with the same mix: each stratum is shuffled and dealt in proportion."""
    r = random.Random(seed + 7)
    by = {s: [x for x in recs if x["stratum"] == s] for s in QUOTA}
    for xs in by.values():
        r.shuffle(xs)
    n_rounds = TOTAL // ROUND_SIZE
    rounds: list[list[dict]] = [[] for _ in range(n_rounds)]
    for xs in by.values():
        per = len(xs) // n_rounds
        for i in range(n_rounds):
            rounds[i] += xs[i * per : (i + 1) * per]
    for rd in rounds:
        r.shuffle(rd)
    return rounds


def exclusion_set(root: Path):
    paths = [root / p for p in EXCLUSION_PATHS] + [LIBPOSTAL_TESTS]
    return exclusions.load([p for p in paths if p.exists()])


def round_lines(rounds, tag: str, key: str = "text") -> list[str]:
    """The text of each round file, as `write` lays it out."""
    return [
        "\n".join(
            json.dumps({"id": f"{tag}-r{i}-{j:03d}", "text": x[key]}, ensure_ascii=False) for j, x in enumerate(rd, 1)
        )
        + "\n"
        for i, rd in enumerate(rounds, 1)
    ]


R9_BEGIN, R9_END = "<!-- round-9 begin -->", "<!-- round-9 end -->"


def restore_round(
    root: Path, seed: int, banned: set[str], out: Path, real_dir: Path, tag: str, confirm: bool, twin: bool
):
    """Round 9 (issue #26): redraw, check rounds 1 to 6 reproduce, then write the restored rows' own text (private)."""
    skipped: list[dict] = []
    recs, dropped = build(root, seed, banned, skipped)
    rounds = deal(recs, seed)
    for i, body in enumerate(round_lines(rounds, tag), 1):
        p = out / "rounds" / f"round-{i}.jsonl"
        if not p.exists() or p.read_text(encoding="utf-8") != body:
            raise SystemExit(f"round {i}: the draw does not reproduce {p}; nothing written")
    rrecs, rdrop = restore(skipped, recs, seed, banned)
    body = (
        "\n".join(
            json.dumps({"id": f"{tag}-r9-{j:03d}", "text": x["real"]}, ensure_ascii=False)
            for j, x in enumerate(rrecs, 1)
        )
        + "\n"
    )
    by = collections.Counter(f"{x['stratum']}/{x['source']}" for x in rrecs)
    print(f"rounds 1 to 6 reproduced; walk dropped {len(skipped)} as leak-or-unfaithful; round 9: {len(rrecs)} records")
    print(
        f"by stratum/source: {dict(sorted(by.items()))}; dropped again (not parser behavior): {dict(sorted(rdrop.items()))}"
    )
    real = real_dir / "rounds" / "round-9.jsonl"
    if real.exists():
        print(
            "round 9 file " + ("reproduced" if real.read_text(encoding="utf-8") == body else "DIFFERS from this draw")
        )
    if not confirm:
        print("(dry run: pass --confirm to write)")
        return
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(body, encoding="utf-8")
    pl = [
        json.dumps(
            {
                "id": f"{tag}-r9-{j:03d}",
                "round": 9,
                **{k: x[k] for k in ("stratum", "source", "shape", "style")},
                "restored": True,
            }
        )
        for j, x in enumerate(rrecs, 1)
    ]
    if twin:
        (out / "provenance-r9.jsonl").write_text("\n".join(pl) + "\n", encoding="utf-8")
        print(f"wrote {real} and {out / 'provenance-r9.jsonl'}")
        return
    pp = out / "provenance.jsonl"
    kept = [x for x in pp.read_text().splitlines() if x.strip() and json.loads(x)["round"] != 9]
    pp.write_text("\n".join(kept + pl) + "\n", encoding="utf-8")
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    cnt = lambda key: "\n".join(  # noqa: E731
        f"| {k} | {v} |" for k, v in sorted(collections.Counter(x[key] for x in rrecs).items())
    )
    block = f"""{R9_BEGIN}
## Round 9 (restored rows, issue #26)

Seed {seed}, drawn by `tools/golden/sample.py --restore`: {len(rrecs)} unlabeled records, the rows the seed-{seed} walk
dropped as `leak-or-unfaithful` (the `Anonymizer` filter), taken in the same hash order and with the same style rule, and
no anonymizer call on them. Rounds 1 to 6 are unchanged (the redraw reproduces them byte for byte). The duplicate and
exclusion-corpus drops stay: {json.dumps(dict(sorted(rdrop.items())))}. Each record keeps the stratum and source of its
walk and has `restored: true` in `provenance.jsonl`.

**No text ships for this round.** These rows are not anonymized, so `sets/golden/rounds/round-9.jsonl` does not exist;
the cards are labeled on the row's own text (`local-data/golden-real/rounds/round-9.jsonl`, git-ignored) and the shipped
text is made from the labels by `tools/golden/derive.py`, which holds a card back when a real word is left outside a
kept label (the count held is added here after derivation).

- ids of round 9 (`provenance.jsonl` rows with `round` 9), SHA-256 of those rows: `{sha(chr(10).join(pl).encode())}`
- `provenance.jsonl` (all rounds): `{sha(pp.read_bytes())}`

| Stratum | Records |
|---|---|
{cnt("stratum")}

| Source | Records |
|---|---|
{cnt("source")}

| Style | Records |
|---|---|
{cnt("style")}
{R9_END}
"""
    mp = out / "MANIFEST.md"
    md = re.sub(rf"\n?{re.escape(R9_BEGIN)}.*?{re.escape(R9_END)}\n?", "", mp.read_text(encoding="utf-8"), flags=re.S)
    mp.write_text(md.rstrip("\n") + "\n\n" + block, encoding="utf-8")
    print(f"wrote {real}; {len(pl)} provenance rows and the manifest section updated")


def write_real(rounds, out: Path, real_dir: Path, tag: str) -> None:
    """The unmasked rounds, after checking that this draw reproduces the committed (anonymized) rounds exactly."""
    for i, body in enumerate(round_lines(rounds, tag), 1):
        p = out / "rounds" / f"round-{i}.jsonl"
        if not p.exists() or p.read_text(encoding="utf-8") != body:
            raise SystemExit(f"round {i}: the draw does not reproduce {p}; nothing written")
    (real_dir / "rounds").mkdir(parents=True, exist_ok=True)
    for i, body in enumerate(round_lines(rounds, tag, "real"), 1):
        (real_dir / "rounds" / f"round-{i}.jsonl").write_text(body, encoding="utf-8")
    changed = sum(x["real"] != x["text"] for rd in rounds for x in rd)
    print(f"draw reproduced; wrote {len(rounds)} unmasked rounds to {real_dir / 'rounds'} ({changed} cards differ)")


def write(rounds, out: Path, tag: str, seed_note: str, counts, dropped):
    (out / "rounds").mkdir(parents=True, exist_ok=True)
    prov, sums = [], {}
    for i, rd in enumerate(rounds, 1):
        lines = []
        for j, x in enumerate(rd, 1):
            gid = f"{tag}-r{i}-{j:03d}"
            lines.append(json.dumps({"id": gid, "text": x["text"]}, ensure_ascii=False))
            prov.append({"id": gid, "round": i, **{k: x[k] for k in ("stratum", "source", "shape", "style")}})
        p = out / "rounds" / f"round-{i}.jsonl"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        sums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (out / "provenance.jsonl").write_text("\n".join(json.dumps(p) for p in prov) + "\n", encoding="utf-8")
    sums["provenance.jsonl"] = hashlib.sha256((out / "provenance.jsonl").read_bytes()).hexdigest()
    return prov, sums


def manifest(out: Path, prov, sums, seed_note, counts, dropped):
    def table(key):
        c = collections.Counter(p[key] for p in prov)
        return "\n".join(f"| {k} | {v:,} |" for k, v in sorted(c.items()))

    md = f"""# Golden set: manifest

{seed_note}. {len(prov):,} unlabeled records in {len(sums) - 1} rounds of {ROUND_SIZE}, drawn by `tools/golden/sample.py`
(composition: `COMPOSITION.md`). doorplate {importlib.metadata.version("doorplate")} supplied the anonymizer. Every
address is invented or anonymized: house numbers and street names are made up; city, state and ZIP are real.
This set is not "home" for any parser. It has no labels yet (steps 3 onward).

## Checksums (SHA-256)

{chr(10).join(f"- `{k}`: `{v}`" for k, v in sums.items())}

## Records by stratum

| Stratum | Records |
|---|---|
{table("stratum")}

## Records by source

| Source | Records |
|---|---|
{table("source")}

## Records by shape

| Shape | Records |
|---|---|
{table("shape")}

## Records by style

| Style | Records |
|---|---|
{table("style")}

## Exclusion string check

Every record was compared (lowercase, letters and digits only; whole text and first line) with {len(counts) - 0} corpus
locations; passes. Strings read per location:

{chr(10).join(f"- `{k}`: {v:,}" for k, v in counts.items())}

Candidates dropped while drawing (counts only): {json.dumps(dict(sorted(dropped.items())))}.
libpostal's training data is not on disk here and could not be checked; its test sources under `src/test` were.
"""
    (out / "MANIFEST.md").write_text(md, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(
        "--twin", action="store_true", help="the private twin: unpublished seed, writes to doorplate's local-data"
    )
    ap.add_argument("--check", action="store_true", help="re-check the committed rounds against the exclusion corpora")
    ap.add_argument("--real", action="store_true", help="write the unmasked text of the same draw (for labeling)")
    ap.add_argument(
        "--restore", action="store_true", help="round 9: the rows the anonymizer filter dropped (issue #26)"
    )
    ap.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    a = ap.parse_args()
    root = a.private_root

    if a.check:
        banned, counts = exclusion_set(root)
        bad = 0
        paths = sorted((ROOT / "sets/golden/rounds").glob("round-*.jsonl"))
        for p in paths + sorted((ROOT / "sets/golden/gold").glob("round-*.jsonl")):
            bad += sum(exclusions.hit(json.loads(line)["text"], banned) for line in p.read_text().splitlines())
        print(f"{len(banned):,} corpus strings from {len(counts)} locations; {bad} golden records match")
        raise SystemExit(1 if bad else 0)

    if a.twin:
        tdir = root / "local-data/golden-twin"
        seed_file = tdir / "SEED"
        out, tag = tdir, "t"
        if seed_file.exists():
            seed = int(seed_file.read_text())
        elif a.confirm:
            tdir.mkdir(parents=True, exist_ok=True)
            seed = secrets.randbelow(10**9) + 10**9
            seed_file.write_text(str(seed))
        else:
            seed = 0
        note = "Private twin (not published)"
    else:
        seed, out, tag = PUBLIC_SEED, ROOT / "sets/golden", "g"
        note = f"Seed {PUBLIC_SEED}"
    print(
        f"plan: {TOTAL} records in rounds of {ROUND_SIZE}: {QUOTA}; public sources {PUBLIC_SOURCES}; "
        f"oversample x{OVERSAMPLE}; output {out}"
    )
    if not a.confirm and not a.restore:
        print("(dry run: pass --confirm to write)")
        return
    banned, counts = exclusion_set(root)
    print(f"exclusion set: {len(banned):,} strings from {len(counts)} locations")
    if a.twin:  # the twin must not repeat a public record either
        for p in (ROOT / "sets/golden/rounds").glob("round-*.jsonl"):
            banned |= {exclusions.norm(json.loads(line)["text"]) for line in p.read_text().splitlines()}
    if a.restore:
        restore_round(root, seed, banned, out, out / "real" if a.twin else REAL_DIR, tag, a.confirm, a.twin)
        return
    recs, dropped = build(root, seed, banned)
    rounds = deal(recs, seed)
    if a.real:
        write_real(rounds, out, out / "real" if a.twin else REAL_DIR, tag)
        return
    prov, sums = write(rounds, out, tag, note, counts, dropped)
    manifest(out, prov, sums, note, counts, dropped)
    print(f"wrote {len(prov)} records in {len(rounds)} rounds to {out}; dropped {sum(dropped.values()):,} candidates")


if __name__ == "__main__":
    main()
