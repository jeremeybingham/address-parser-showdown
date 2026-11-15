#!/usr/bin/env python3
"""Draw round 12 (real replacements for the cards the owner removed from rounds 7 and 8) and pre-label it from the source.

    uv run python -m tools.golden.realforms             # dry run: counts per class, nothing written
    uv run python -m tools.golden.realforms --confirm   # writes the private round, its provenance rows and the pre-labels

Three well-formed classes, real rows only (the invented strings of round 8 could not be checked on a map or labeled by hand):

| class | source | forms |
|---|---|---|
| `grid-utah` (10) | NAD, Utah | `123 W 400 S` (covered, directions abbreviated) and `123 West 400 South` (adjacent, as the source writes them) |
| `grid-wisconsin` (8) | NAD, Wisconsin | `W399S10635 Connor Dr`: the whole `W399S10635` is the house number (owner decision, 2026-11-14), as written |
| `military` (12) | FCC amateur licenses | `PSC 123 BOX 4567, APO AE 09012` (covered, 6) and the `CMR` / `UNIT` forms (adjacent, 3 + 3) |

Mangled military lines and anything outside these forms are never drawn. Rows are picked by a seeded hash of the row (never
by what a parser does with them); duplicates of any earlier round and exclusion-corpus hits are dropped. The labels come
from the source's own fields (NAD's split columns, a fixed regular expression for the military line): no parser is run
and nothing here reads a parser's output. Each card is saved to the round log with phase `prelabel` and a revisit mark, so
`server revisit` lists them for the owner to glance at and clear. Prints counts and shapes, never a record; reader errors
print only the error type. The text stays in the git-ignored `local-data/`; `derive.py` makes the shipped text.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.golden import exclusions, sample  # noqa: E402
from tools.label import store  # noqa: E402

SEED = 20261115
ROUND = 12
OVERSAMPLE = 40
ABBR = {"North": "N", "South": "S", "East": "E", "West": "W"}
OUT = sample.REAL_DIR / "rounds/round-12.jsonl"
NAD = "local-data/nad-2026/nad_r24.parquet"
FCC = "local-data/fcc-uls-amateur-2026/en_addr.parquet"
NO_EXTRA = " and ".join(
    f"coalesce({c}, '') = ''"
    for c in ("AddNum_Suf", "St_PreMod", "St_PreTyp", "St_PreSep", "St_PosMod", "Building", "Floor", "Unit", "Room", "SubAddress")
)  # fmt: skip
NAD_COLS = "AddNo_Full, St_PreDir, St_Name, St_PosTyp, St_PosDir, Post_City, State, Zip_Code"
MIL = re.compile(r"^(PSC|CMR|UNIT) (\d+),? BOX (\d+)$")


def build(parts: list[tuple[str, str | None]]) -> tuple[str, list[list]]:
    """Join words with spaces (a `None` label is punctuation or glue) and return the text and its spans."""
    text, spans = "", []
    for word, label in parts:
        if text and not word.startswith(","):
            text += " "
        if label:
            spans.append([len(text), len(text) + len(word), label])
        text += word
    return text, spans


def last_line(city: str, st: str, z: str) -> list[tuple[str, str | None]]:
    return [(city.strip().title() + ",", None), (st, "state"), (z[:5], "postal_code")]


def city_part(city: str) -> tuple[str, str]:
    return (city.strip().title(), "city")


def tail(city: str, st: str, z: str):
    return [(",", None), city_part(city), (",", None), (st, "state"), (z[:5], "postal_code")]


def card_text(head: list[tuple[str, str | None]], city: str, st: str, z: str, upper_city: bool = False):
    """Street line, comma, city, comma, state ZIP, with the spans of the labeled words."""
    text, spans = build(head)
    c = city.strip().upper() if upper_city else city.strip().title()
    s = f"{text}, "
    spans.append([len(s), len(s) + len(c), "city"])
    s += c + ", "
    spans.append([len(s), len(s) + 2, "state"])
    s += st + " "
    spans.append([len(s), len(s) + 5, "postal_code"])
    return s + z[:5], spans


def nad_rows(con, state: str, where: str, size: int):
    q = (
        f"select {NAD_COLS} from read_parquet('{sample.DEFAULT_PRIVATE / NAD}') where State = '{state}' and {NO_EXTRA}"
        f" and Post_City is not null and regexp_matches(coalesce(Zip_Code, ''), '^[0-9]{{5}}') and {where}"
    )
    return sample.top_by_hash(
        con, f"({q})", "true", NAD_COLS.split(", "), SEED + (1 if state == "UT" else 2), size, "*"
    )


def utah(con, want: int):
    """Each row with both forms: abbreviated directions (covered) and as the source writes them (adjacent)."""
    where = (
        "regexp_matches(AddNo_Full, '^[0-9]+$') and regexp_matches(St_Name, '^[0-9]+$') and coalesce(AddNum_Pre, '') = '' "
        "and St_PreDir in ('North','South','East','West') and St_PosDir in ('North','South','East','West') "
        "and coalesce(St_PosTyp, '') = ''"
    )
    out = []
    for num, pre, name, _pt, post, city, st, z in nad_rows(con, "UT", where, want * OVERSAMPLE):
        forms = {}
        for variant, (a, b) in (("covered", (ABBR[pre], ABBR[post])), ("adjacent", (pre, post))):
            head = [
                (num, "house_number_value"),
                (a, "street_pre_direction"),
                (name, "street_name"),
                (b, "street_post_direction"),
            ]
            forms[variant] = card_text(head, city, st, z)
        out.append(forms)
    return out


def wisconsin(con, want: int):
    where = "regexp_matches(AddNo_Full, '^[NSEW][0-9]+[NSEW][0-9]+$') and St_Name is not null"
    out = []
    for num, pre, name, ptype, post, city, st, z in nad_rows(con, "WI", where, want * OVERSAMPLE):
        head = [(num, "house_number_value")]
        if pre:
            head.append((ABBR.get(pre, pre), "street_pre_direction"))
        head.append((name, "street_name"))
        if ptype:
            head.append((ptype, "street_post_type"))
        if post:
            head.append((ABBR.get(post, post), "street_post_direction"))
        text, spans = card_text(head, city, st, z)
        out.append((text, spans, "grid-wisconsin", "adjacent", "nad"))
    return out


def military(con, kinds: dict[str, int]):
    q = (
        f"select street_address, city, state, zip_code from read_parquet('{sample.DEFAULT_PRIVATE / FCC}') "
        "where upper(city) in ('APO','FPO','DPO') and state in ('AA','AE','AP') "
        "and regexp_matches(coalesce(zip_code,''), '^[0-9]{5}')"
    )
    rows = sample.top_by_hash(
        con, f"({q})", "true", ["street_address", "city", "state", "zip_code"], SEED + 3, 5000, "*"
    )
    out = []
    for line, city, st, z in rows:
        m = MIL.match(re.sub(r"\s+", " ", (line or "").strip().upper()))
        if not m:
            continue
        kind = m.group(1)
        t, n, box = m.groups()
        head = [(t, "route_type"), (n, "route_value"), ("BOX", "route_box_type"), (box, "route_box_value")]
        text, spans = build(head)
        text += ", "  # the Publication 28 form: no comma between the post office, the state and the ZIP
        for word, label in ((city.strip().upper(), "city"), (st, "state"), (z[:5], "postal_code")):
            spans.append([len(text), len(text) + len(word), label])
            text += word + " "
        text, spans = text.rstrip(), spans
        out.append((text.upper(), spans, "military", "covered" if kind == "PSC" else "adjacent", kind))
    return out


def draw():
    import duckdb

    con = duckdb.connect()
    banned, _ = sample.exclusion_set(sample.DEFAULT_PRIVATE)
    for p in sorted((ROOT / "sets/golden/rounds").glob("round-*.jsonl")) + sorted(
        (sample.REAL_DIR / "rounds").glob("round-[0-9]*.jsonl")
    ):
        if p.name != "round-12.jsonl":
            banned |= {exclusions.norm(json.loads(x)["text"]) for x in p.read_text(encoding="utf-8").splitlines()}
    plan = {  # class -> {bucket: count}; a bucket is a variant (and for military the line type)
        "grid-utah": {"covered": 5, "adjacent": 5},
        "grid-wisconsin": {"adjacent": 8},
        "military": {"PSC": 6, "CMR": 3, "UNIT": 3},
    }
    pools = {
        "grid-utah": [[(*f[v], "grid-utah", v, "nad") for v in ("covered", "adjacent")] for f in utah(con, 10)],
        "grid-wisconsin": [[x] for x in wisconsin(con, 8)],
        "military": [[x] for x in military(con, plan["military"])],
    }
    out, dropped, seen = [], collections.Counter(), set()
    for cls, want in plan.items():
        left = dict(want)
        bucket_of = lambda o, cls=cls: o[4] if cls == "military" else o[3]  # noqa: E731
        for options in pools[cls]:
            opts = [o for o in options if left.get(bucket_of(o))]
            if not opts:
                continue
            # a Utah row serves whichever variant still needs the most cards
            text, spans, shape, variant, kind = max(opts, key=lambda o: left[bucket_of(o)])
            k = exclusions.norm(text)
            if k in seen:
                dropped["duplicate"] += 1
            elif k in banned or exclusions.hit(text, banned):
                dropped["excluded"] += 1
            else:
                seen.add(k)
                left[bucket_of((0, 0, 0, variant, kind))] -= 1
                src = "fcc-amateur" if cls == "military" else "nad"
                out.append({"text": text, "spans": spans, "shape": shape, "variant": variant, "source": src})
        if any(left.values()):
            raise SystemExit(f"{cls}: not enough rows for {left}; raise OVERSAMPLE")
    for j, x in enumerate(out, 1):
        x["id"] = f"g-r{ROUND}-{j:03d}"
    return out, dropped


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    try:
        cards, dropped = draw()
    except SystemExit:
        raise
    except Exception as e:  # DuckDB errors quote source rows
        raise SystemExit(f"draw failed: {type(e).__name__}") from None
    by = collections.Counter((x["shape"], x["variant"]) for x in cards)
    print(
        f"round 12: {len(cards)} cards (seed {SEED}); dropped {dict(dropped)}; per class and variant {dict(sorted(by.items()))}"
    )
    body = "\n".join(json.dumps({"id": x["id"], "text": x["text"]}, ensure_ascii=False) for x in cards) + "\n"
    if OUT.exists():
        print(
            "round 12 file " + ("reproduced" if OUT.read_text(encoding="utf-8") == body else "DIFFERS from this draw")
        )
    if not a.confirm:
        print("(dry run: pass --confirm to write)")
        return
    OUT.write_text(body, encoding="utf-8")
    for x in cards:  # pre-labels, only for a card with no saved label yet
        if x["id"] not in store.load_log(ROUND):
            store.save_card(
                ROUND,
                x,
                {"spans": x["spans"], "revisit": True, "note": "pre-labeled from the source fields"},
                phase="prelabel",
            )
    pp = ROOT / "sets/golden/provenance.jsonl"
    rows = [json.loads(x) for x in pp.read_text().splitlines() if x.strip() and json.loads(x)["round"] != ROUND]
    rows += [
        {
            "id": x["id"],
            "round": ROUND,
            "stratum": "real",
            "source": x["source"],
            "shape": x["shape"],
            "style": "as-written",
            "variant": x["variant"],
            "replacement": True,
        }
        for x in cards
    ]
    pp.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
    print(f"wrote {OUT}, {len(cards)} pre-labels and provenance rows")


if __name__ == "__main__":
    main()
