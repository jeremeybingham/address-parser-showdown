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


def placeholder_phrases(root: Path) -> set[str]:
    """doorplate's list of stand-ins for a missing city (`NOT STATED`, `UNKNOWN`, ...), from its special.toml."""
    import tomllib

    path = root / "crates/doorplate/data/special.toml"
    return set(tomllib.loads(path.read_text(encoding="utf-8"))["city_placeholder"]["phrases"])


def is_placeholder(city: str, phrases: set[str]) -> bool:
    """True when the whole city field is a placeholder phrase (case and extra spaces do not matter)."""
    return " ".join(city.upper().split()) in phrases


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
        out.append((" ".join(p.strip() for p in parts if p.strip()), city.strip().title(), st, zipc[:5], None))
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
        raw = (r[-3].strip(), r[-2].strip(), r[-1].strip())  # the source's own city, state and ZIP (kept in round 9)
        out.append((street, r[-3].strip().title(), r[-2].upper(), r[-1][:5], raw))
    return out


def build(
    root: Path,
    seed: int,
    banned: set[str],
    skipped: list[dict] | None = None,
    replacements: list[dict] | None = None,
):
    """All records as dicts (text, stratum, source, shape, style), before rounds.

    `skipped`, if given, receives the rows the walk dropped as leak-or-unfaithful (round 9, `restore`).
    Every record has `city_placeholder`. `replacements`, if given, receives one new record (`replacement: True`) for each
    record with a placeholder city (round 11): the next unused rows of the same source's walk, own random generator."""
    r = random.Random(seed)
    con = duckdb.connect()
    recs: list[dict] = []
    seen: set[str] = set()
    dropped = collections.Counter()

    phrases = placeholder_phrases(root)
    rest: dict[tuple[str, str], list] = {}

    def add(stratum, source, text, shape, sty, real=None, city=""):
        k = exclusions.norm(text)
        if k in seen:
            dropped[f"{source}:duplicate"] += 1
            return False
        if exclusions.hit(text, banned):
            dropped[f"{source}:excluded"] += 1
            return False
        seen.add(k)
        recs.append(
            {
                "text": text,
                "real": real or text,
                "stratum": stratum,
                "source": source,
                "shape": shape,
                "style": sty,
                "city_placeholder": is_placeholder(city, phrases),
            }
        )
        return True

    def take(stratum, source, rows, want, shape, force_style=None):
        streets = anonymize([x[0] for x in rows], seed)
        n = 0
        for i, ((street, city, st, z, raw), anon) in enumerate(zip(rows, streets, strict=True)):
            if n >= want:
                rest[(stratum, source)] = list(zip(rows, streets, strict=True))[i:]
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
                            "raw": raw,
                        }
                    )
                continue
            text, sty = style(r, anon, city, st, z, force_style)
            real, _ = style(r, street, city, st, z, sty)  # a named style draws nothing from r: the draw is unchanged
            n += add(stratum, source, text, shape, sty, real, city)
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
    if replacements is not None:
        r2 = random.Random(seed + 11)
        for (stratum, source), want in sorted(
            collections.Counter((x["stratum"], x["source"]) for x in recs if x["city_placeholder"]).items()
        ):
            n = 0
            for (street, city, st, z, _raw), anon in rest[(stratum, source)]:
                if n >= want:
                    break
                if anon is None or is_placeholder(city, phrases):
                    dropped[f"{source}:replacement-skipped"] += 1
                    continue
                text, sty = style(r2, anon, city, st, z, "mixed-commas" if stratum == "clean" else None)
                real, _ = style(r2, street, city, st, z, sty)
                if add(stratum, source, text, "ordinary" if stratum == "clean" else "as-found", sty, real, city):
                    replacements.append({**recs.pop(), "replacement": True})
                    n += 1
            if n < want:
                raise SystemExit(f"{source}: only {n} of {want} replacements; raise OVERSAMPLE")
        r2.shuffle(replacements)
    return recs, dropped


def restore(skipped: list[dict], recs: list[dict], seed: int, banned: set[str], phrases: set[str]):
    """Round 9: the rows the walk dropped as leak-or-unfaithful, on their own text (no anonymizer call here).

    A row of a messy source keeps the source's own city, state and ZIP (case, ZIP+4) and gets no dice style (`as-written`);
    NAD rows keep the draw's style rule.

    Own random generator, so rounds 1 to 6 are untouched. Duplicates (of a kept row's own text or of each other) and
    exclusion-corpus hits are dropped as before; they are not parser behavior. Returns (records, dropped counts)."""
    r = random.Random(seed + 9)
    seen = {exclusions.norm(x["real"]) for x in recs}
    out, dropped = [], collections.Counter()
    for x in skipped:
        street, city, st, z = x["row"]
        if x["raw"]:  # a messy source: the line as the source has it (case, ZIP+4), no dice style (issue #26, item 3)
            text, sty = f"{street}, {x['raw'][0]}, {x['raw'][1]} {x['raw'][2]}", "as-written"
        else:
            sty = x["force"] or weighted(r, STYLES)
            text, _ = style(r, street, city, st, z, sty)
        k = exclusions.norm(text)
        if is_placeholder(x["raw"][0] if x["raw"] else city, phrases):
            dropped[f"{x['source']}:placeholder-city"] += 1
        elif k in seen:
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
        for j, x in enumerate(rd, 1):
            x["idx"] = j  # the card's number in its round, kept when a placeholder-city card is dropped
    return rounds


def final_rounds(rounds, replacements):
    """Rounds 1 to 6 without the placeholder-city cards (ids keep their gaps), then round 11 (their replacements)."""
    kept = [[x for x in rd if not x["city_placeholder"]] for rd in rounds]
    for j, x in enumerate(replacements, 1):
        x["idx"] = j
    return {**{i: rd for i, rd in enumerate(kept, 1)}, 11: replacements}


def exclusion_set(root: Path):
    paths = [root / p for p in EXCLUSION_PATHS] + [LIBPOSTAL_TESTS]
    return exclusions.load([p for p in paths if p.exists()])


def round_lines(rounds, tag: str, key: str = "text") -> dict[int, str]:
    """The text of each round file, as `write` lays it out (`rounds`: round number -> cards, each with its `idx`)."""
    return {
        i: "\n".join(json.dumps({"id": f"{tag}-r{i}-{x['idx']:03d}", "text": x[key]}, ensure_ascii=False) for x in rd)
        + "\n"
        for i, rd in rounds.items()
    }


R9_BEGIN, R9_END = "<!-- round-9 begin -->", "<!-- round-9 end -->"


def restore_round(
    root: Path, seed: int, banned: set[str], out: Path, real_dir: Path, tag: str, confirm: bool, twin: bool
):
    """Round 9 (issue #26): redraw, check rounds 1 to 6 reproduce, then write the restored rows' own text (private)."""
    skipped: list[dict] = []
    reps: list[dict] = []
    recs, dropped = build(root, seed, banned, skipped, reps)
    rounds = final_rounds(deal(recs, seed), reps)
    for i, body in round_lines(rounds, tag).items():
        p = out / "rounds" / f"round-{i}.jsonl"
        if not p.exists() or p.read_text(encoding="utf-8") != body:
            raise SystemExit(f"round {i}: the draw does not reproduce {p}; nothing written")
    rrecs, rdrop = restore(skipped, recs, seed, banned, placeholder_phrases(root))
    body = (
        "\n".join(
            json.dumps({"id": f"{tag}-r9-{j:03d}", "text": x["real"]}, ensure_ascii=False)
            for j, x in enumerate(rrecs, 1)
        )
        + "\n"
    )
    by = collections.Counter(f"{x['stratum']}/{x['source']}" for x in rrecs)
    print(
        f"rounds 1 to 6 and 11 reproduced; walk dropped {len(skipped)} as leak-or-unfaithful; round 9: {len(rrecs)} records"
    )
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
dropped as `leak-or-unfaithful` (the `Anonymizer` filter), taken in the same hash order, and
no anonymizer call on them. A row of a messy source keeps the source's own city, state and ZIP (case, ZIP+4) with no dice
style (style `as-written`, issue #26 item 3); NAD rows keep the draw's style rule. Rounds 1 to 6 are unchanged (the redraw reproduces them byte for byte). The duplicate and
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


R11_BEGIN, R11_END = "<!-- round-11 begin -->", "<!-- round-11 end -->"


def drop_placeholders(root: Path, seed: int, banned: set[str], out: Path, tag: str, confirm: bool) -> None:
    """One-time change (2026-11-14): drop the cards whose city is a placeholder from rounds 1 to 6; add their replacements.

    Redraws, checks that the unchanged draw reproduces the committed rounds 1 to 6, then writes rounds 1 to 6 without the
    placeholder-city cards (ids keep their gaps, so labels of the other cards stay valid), round 11 (one replacement per
    dropped card), `provenance.jsonl` and the manifest. Run `--real` afterwards for the unmasked text."""
    reps: list[dict] = []
    recs, dropped = build(root, seed, banned, None, reps)
    full = deal(recs, seed)
    final = final_rounds(full, reps)
    new = round_lines(final, tag)
    path = lambda i: out / "rounds" / f"round-{i}.jsonl"  # noqa: E731
    if all(path(i).exists() and path(i).read_text(encoding="utf-8") == body for i, body in new.items()):
        print("rounds 1 to 6 and 11 are already the filtered draw; nothing to do")
        return
    old = round_lines(dict(enumerate(full, 1)), tag)
    for i, body in old.items():
        if path(i).read_text(encoding="utf-8") != body:
            raise SystemExit(f"round {i}: the unfiltered draw does not reproduce {path(i)}; nothing written")
    gone = [f"{tag}-r{i}-{x['idx']:03d}" for i, rd in enumerate(full, 1) for x in rd if x["city_placeholder"]]
    by = collections.Counter(f"{x['stratum']}/{x['source']}" for rd in full for x in rd if x["city_placeholder"])
    print(f"unfiltered draw reproduced; {len(gone)} placeholder-city cards: {dict(sorted(by.items()))}")
    print(f"round 11: {len(reps)} replacements; dropped while drawing: {dict(sorted(dropped.items()))}")
    if not confirm:
        print("(dry run: pass --confirm to write)")
        return
    for i, body in new.items():
        path(i).write_text(body, encoding="utf-8")
    pp = out / "provenance.jsonl"
    rows = [json.loads(x) for x in pp.read_text().splitlines() if x.strip()]
    rows = [x for x in rows if x["id"] not in set(gone) and x["round"] != 11]
    rows += [
        {
            "id": f"{tag}-r11-{x['idx']:03d}",
            "round": 11,
            **{k: x[k] for k in ("stratum", "source", "shape", "style")},
            "replacement": True,
        }
        for x in reps
    ]
    pp.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    mp = out / "MANIFEST.md"
    if not mp.exists():
        return
    md = mp.read_text(encoding="utf-8")
    md = re.sub(rf"\n?{re.escape(R11_BEGIN)}.*?{re.escape(R11_END)}\n?", "", md, flags=re.S)
    for i in range(1, 7):
        md = re.sub(rf"(- `round-{i}\.jsonl`: `)[0-9a-f]{{64}}", rf"\g<1>{sha(path(i).read_bytes())}", md, count=1)
    md = re.sub(
        r"(- `provenance\.jsonl` \(all rounds, current\): `)[0-9a-f]{64}", rf"\g<1>{sha(pp.read_bytes())}", md, count=1
    )
    base = [x for x in rows if x["round"] <= 6]
    for name in ("stratum", "source", "shape", "style"):
        table = "\n".join(f"| {k} | {v:,} |" for k, v in sorted(collections.Counter(x[name] for x in base).items()))
        md = re.sub(
            rf"(## Records by {name}\n\n\|[^\n]*\|\n\|---\|---\|\n).*?(\n\n)",
            lambda m, table=table: m.group(1) + table + m.group(2),
            md,
            count=1,
            flags=re.S,
        )
    block = f"""{R11_BEGIN}
## Placeholder-city cards dropped, round 11 added (2026-11-14)

The National Address Database holds a placeholder (`Not stated`) in its city field for some rows. A card whose whole city
field is one of doorplate's `[city_placeholder]` phrases (`crates/doorplate/data/special.toml`) is not part of the set.
{len(gone)} cards of rounds 1 to 6 were dropped ({json.dumps(dict(sorted(by.items())))}); their ids are not reused, so the
other cards keep their ids and labels. Round 11 holds {len(reps)} replacements, the next unused rows of the same sources'
walks (same stratum and source as the card each replaces; own random generator `seed + 11`; no placeholder city, a
duplicate or an exclusion hit skipped). Rounds 1 to 6 now hold {sum(len(rd) for rd in final.values()) - len(reps)}
cards, round 11 {len(reps)}. Round 9 drops its placeholder-city rows as well (counted in its section).

- `round-11.jsonl`: `{sha(path(11).read_bytes())}`
- `provenance.jsonl` (all rounds): `{sha(pp.read_bytes())}`
{R11_END}
"""
    mp.write_text(md.rstrip("\n") + "\n\n" + block, encoding="utf-8")
    print(f"wrote {len(new)} round files, {len(rows)} provenance rows and the manifest")


def write_real(rounds, out: Path, real_dir: Path, tag: str) -> None:
    """The unmasked rounds, after checking that this draw reproduces the committed (anonymized) rounds exactly."""
    for i, body in round_lines(rounds, tag).items():
        p = out / "rounds" / f"round-{i}.jsonl"
        if not p.exists() or p.read_text(encoding="utf-8") != body:
            raise SystemExit(f"round {i}: the draw does not reproduce {p}; nothing written")
    (real_dir / "rounds").mkdir(parents=True, exist_ok=True)
    for i, body in round_lines(rounds, tag, "real").items():
        (real_dir / "rounds" / f"round-{i}.jsonl").write_text(body, encoding="utf-8")
    changed = sum(x["real"] != x["text"] for rd in rounds.values() for x in rd)
    print(f"draw reproduced; wrote {len(rounds)} unmasked rounds to {real_dir / 'rounds'} ({changed} cards differ)")


def write(rounds, out: Path, tag: str, seed_note: str, counts, dropped):
    (out / "rounds").mkdir(parents=True, exist_ok=True)
    prov, sums = [], {}
    for i, rd in rounds.items():
        lines = []
        for x in rd:
            gid = f"{tag}-r{i}-{x['idx']:03d}"
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
    ap.add_argument(
        "--drop-placeholders",
        action="store_true",
        help="rounds 1 to 6 without the placeholder-city cards, plus round 11 (their replacements); one-time",
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
    if not a.confirm and not a.restore and not a.drop_placeholders:
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
    if a.drop_placeholders:
        drop_placeholders(root, seed, banned, out, tag, a.confirm)
        return
    reps: list[dict] = []
    recs, dropped = build(root, seed, banned, None, reps)
    rounds = final_rounds(deal(recs, seed), reps)
    if a.real:
        write_real(rounds, out, out / "real" if a.twin else REAL_DIR, tag)
        return
    if (out / "rounds" / "round-1.jsonl").exists():
        raise SystemExit(
            f"{out} is already drawn (a rewrite would drop rounds 7 to 11 from provenance and the manifest)"
        )
    prov, sums = write(rounds, out, tag, note, counts, dropped)
    manifest(out, prov, sums, note, counts, dropped)
    print(f"wrote {len(prov)} records in {len(rounds)} rounds to {out}; dropped {sum(dropped.values()):,} candidates")


if __name__ == "__main__":
    main()
