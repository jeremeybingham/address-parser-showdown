#!/usr/bin/env python3
"""Draw round 10 (issue #29): SBA PPP loans of $150K and over, the borrower's address as the source wrote it.

    uv run python -m tools.golden.sba             # dry run: the draw's counts, nothing written
    uv run python -m tools.golden.sba --confirm   # writes local-data/golden-real/rounds/round-10.jsonl (private)

The source file is `local-data/sba-ppp/public_150k_plus_240930.csv` (public FOIA data; `NOTICE.md` there). Same rules as
round 9 (`sample.py restore`, issue #26 item 3): the row's own street, city, state and ZIP (case and ZIP+4 kept, style
`as-written`), picked by a seeded hash of the row (never by what a parser does with it), duplicates of any earlier round
and exclusion-corpus hits dropped. No public text ships; the cards stay in the git-ignored `local-data/`. Prints counts
and shapes, never a record; reader errors print only the error type.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.golden import exclusions, sample  # noqa: E402

SEED = 20261114
SIZE = 250
OVERSAMPLE = 4
SOURCE = ROOT / "local-data/sba-ppp/public_150k_plus_240930.csv"
OUT = sample.REAL_DIR / "rounds/round-10.jsonl"


def shape(s: str) -> str:
    return "".join("a" if c.isalpha() else "9" if c.isdigit() else c for c in s)


def draw(seed: int = SEED, size: int = SIZE) -> tuple[list[str], collections.Counter]:
    banned, _ = sample.exclusion_set(sample.DEFAULT_PRIVATE)
    for p in sorted((ROOT / "sets/golden/rounds").glob("round-*.jsonl")) + sorted(
        (sample.REAL_DIR / "rounds").glob("round-[0-9].jsonl")
    ):
        banned |= {exclusions.norm(json.loads(line)["text"]) for line in p.read_text(encoding="utf-8").splitlines()}
    states = ",".join(repr(s) for s in sorted(sample.STATES))
    src = f"read_csv('{SOURCE}', all_varchar=true, header=true, ignore_errors=true)"
    import duckdb

    rows = sample.top_by_hash(
        duckdb.connect(),
        src,
        f"length(trim(coalesce(BorrowerAddress,''))) >= 5 and BorrowerCity is not null and upper(BorrowerState) in ({states})"
        " and regexp_matches(coalesce(BorrowerZip,''), '^[0-9]{5}')",
        ["BorrowerAddress", "BorrowerCity", "BorrowerState", "BorrowerZip"],
        seed,
        size * OVERSAMPLE,
        "BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip",
    )
    out, dropped = [], collections.Counter()
    seen: set[str] = set()
    for street, city, st, z in rows:
        text = f"{street.strip()}, {city.strip()}, {st.strip()} {z.strip()}"
        k = exclusions.norm(text)
        if k in seen:
            dropped["duplicate"] += 1
        elif k in banned or exclusions.hit(text, banned):
            dropped["excluded"] += 1
        else:
            seen.add(k)
            out.append(text)
    random.Random(seed).shuffle(out)
    return out[:size], dropped


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    try:
        recs, dropped = draw()
    except Exception as e:  # DuckDB errors quote source rows
        raise SystemExit(f"draw failed: {type(e).__name__}") from None
    if len(recs) < SIZE:
        raise SystemExit(f"only {len(recs)} of {SIZE} records after filters; raise OVERSAMPLE")
    states = collections.Counter(t.rsplit(" ", 2)[-2] for t in recs)
    print(
        f"round 10: {len(recs)} records (seed {SEED}); dropped {dict(dropped)}; {len(states)} states, top {states.most_common(3)}"
    )
    print(f"upper-case lines: {sum(t == t.upper() for t in recs)}; with ZIP+4: {sum(t[-5] == '-' for t in recs)}")
    body = (
        "\n".join(json.dumps({"id": f"g-r10-{j:03d}", "text": t}, ensure_ascii=False) for j, t in enumerate(recs, 1))
        + "\n"
    )
    if OUT.exists():
        print(
            "round 10 file " + ("reproduced" if OUT.read_text(encoding="utf-8") == body else "DIFFERS from this draw")
        )
    if not a.confirm:
        print("(dry run: pass --confirm to write)")
        return
    OUT.write_text(body, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
