"""Make the shipped gold from the private gold: invented values in place of the private ones, labels carried over.

    uv run python -m tools.golden.derive 1 2 3      # rounds to derive (each must be exported: store.export_round)

Labeling is done on the unmasked text (`local-data/golden-real/`), so a hard card can be checked on a map. For a card
drawn from a public record (strata `public` and `clean`), this script replaces the text inside the gold spans of the
labels in `REPLACE` with invented text of the same length and shape: digits by other digits, words by invented words in
the same case; street types, directionals and unit words (`sample.SAFE`) and runs of one or two letters stay. Because
every replacement has the same length, the spans and alternatives are the hand gold unchanged. City, state, ZIP and
every type and direction label stay real, as in the draw (`COMPOSITION.md`). A `non_address` card has its whole text
replaced. Template cards are invented already and ship as labeled.

A card is held back (not shipped) when its derived text keeps a real word of four letters or more outside the kept
labels (label that word, often as `other`, and run again) or still matches an exclusion corpus after five tries. The
output is deterministic. It prints counts and card ids only; a side-by-side review file for the owner goes to
`local-data/golden-real/review/round-N.md` (git-ignored).
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.golden import exclusions, sample  # noqa: E402
from tools.golden.sample import PUBLIC_SEED, SAFE, STATES  # noqa: E402
from tools.label import store  # noqa: E402

REPLACE = {
    "house_number_prefix",
    "house_number_value",
    "street_name",
    "unit_value",
    "po_box_value",
    "route_value",
    "route_box_value",
    "recipient",
    "building_name",
    "other",
}
KEEP_WORDS = {  # labels whose real words may stay in the shipped text
    "street_pre_direction",
    "street_pre_type",
    "street_post_type",
    "street_post_direction",
    "unit_type",
    "po_box_type",
    "route_type",
    "route_box_type",
    "city",
    "state",
    "country",
    "house_number_suffix",
}
# invented words must not read as an address word: SAFE, state codes and common USPS suffix and unit abbreviations
BANNED = (
    SAFE
    | {s.lower() for s in STATES}
    | set(
        [
            "ave",
            "av",
            "st",
            "str",
            "rd",
            "dr",
            "ln",
            "ct",
            "cir",
            "blvd",
            "hwy",
            "pkwy",
            "pl",
            "trl",
            "ter",
            "way",
            "sq",
            "loop",
            "run",
            "row",
            "pike",
            "aly",
            "anx",
            "arc",
            "byp",
            "cv",
            "cyn",
            "est",
            "ext",
            "fwy",
            "gdn",
            "grn",
            "hl",
            "holw",
            "hts",
            "jct",
            "ky",
            "knl",
            "lk",
            "lndg",
            "mdw",
            "mnr",
            "msn",
            "mtn",
            "mt",
            "ft",
            "pt",
            "prt",
            "rdg",
            "riv",
            "shr",
            "spg",
            "spur",
            "sta",
            "stn",
            "trce",
            "trak",
            "tunl",
            "un",
            "vl",
            "vly",
            "vw",
            "xing",
            "apt",
            "bldg",
            "fl",
            "rm",
            "ste",
            "trlr",
            "dept",
            "lbby",
            "lowr",
            "ofc",
            "ph",
            "pier",
            "rear",
            "side",
            "slip",
            "spc",
            "stop",
            "uppr",
            "box",
            "rte",
            "rr",
            "hc",
            "po",
            "cr",
            "fm",
            "sr",
            "us",
            "via",
            "the",
            "and",
            "nor",
            "sou",
            "est",
        ]
    )
)
CONS, VOWELS = "bcdfghjklmnprstvwz", "aeiou"
ORD = re.compile(r"^(st|nd|rd|th)$", re.I)
TOKEN = re.compile(r"[A-Za-z]+|[0-9]+|[^A-Za-z0-9]+")
WORD4 = re.compile(r"[A-Za-z]{4,}")
TRIES = 5


def ordinal(n: int) -> str:
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def same_case(word: str, like: str) -> str:
    if like.isupper():
        return word.upper()
    if like.islower():
        return word.lower()
    return "".join(c.upper() if o.isupper() else c.lower() for c, o in zip(word, like, strict=True))


def invent_word(r: random.Random, n: int, avoid: set[str]) -> str:
    for _ in range(100):
        start = r.random() < 0.5
        w = "".join(r.choice(VOWELS if (i % 2 == 0) != start else CONS) for i in range(n))
        if w not in BANNED and w not in avoid:
            return w
    raise RuntimeError("no invented word")  # pragma: no cover


def invent_digits(r: random.Random, s: str) -> str:
    out = [r.choice("123456789" if i == 0 and s[0] != "0" else "0123456789") for i in range(len(s))]
    return "".join(out)


def replace_span(r: random.Random, piece: str, memo: dict[str, str], avoid: set[str]) -> str:
    """Same length and shape; a word seen before on this card gets the same invented word."""
    toks = TOKEN.findall(piece)
    out: list[str] = []
    for i, t in enumerate(toks):
        if t.isdigit():
            out.append(memo.setdefault(t, invent_digits(r, t)))
        elif t.isalpha():
            if ORD.match(t) and i and toks[i - 1].isdigit():
                out.append(same_case(ordinal(int(out[-1])), t))
            elif len(t) <= 2 or t.lower() in BANNED:
                out.append(t)
            else:
                out.append(same_case(memo.setdefault(t.lower(), invent_word(r, len(t), avoid)), t))
        else:
            out.append(t)
    return "".join(out)


def derive_card(card: dict, salt: int = 0, seed: int = PUBLIC_SEED) -> str:
    """The shipped text of one gold card from a public record (same length as the gold text)."""
    text = card["text"]
    r = random.Random(int(hashlib.sha256(f"{seed}|{card['id']}|{salt}".encode()).hexdigest()[:16], 16))
    avoid = {w.lower() for w in re.findall(r"[A-Za-z]+", text)}
    spans = [[0, len(text), "other"]] if card.get("flag") == "non_address" else card["spans"]
    memo: dict[str, str] = {}
    out, at = [], 0
    for s, e, lab in sorted(spans):
        out.append(text[at:s])
        out.append(replace_span(r, text[s:e], memo, avoid) if lab in REPLACE else text[s:e])
        at = e
    out.append(text[at:])
    new = "".join(out)
    assert len(new) == len(text)
    return new


def leaks(card: dict, new: str) -> set[str]:
    """Real words of four letters or more kept outside the kept labels (none may ship)."""
    text = card["text"]
    kept = {w.lower() for s, e, lab in card["spans"] if lab in KEEP_WORDS for w in WORD4.findall(text[s:e])}
    real = {w.lower() for w in WORD4.findall(text)}
    return ({w.lower() for w in WORD4.findall(new)} & real) - SAFE - kept


def derive_round(n: int, banned: set[str], gold_dir: Path, out_dir: Path, review_dir: Path, prov: dict) -> dict:
    cards = [json.loads(x) for x in (gold_dir / f"round-{n}.jsonl").read_text().splitlines() if x.strip()]
    shipped, review, held = [], [], collections.Counter()
    held_ids: list[str] = []
    for c in cards:
        if prov[c["id"]]["stratum"] == "template":
            new = c["text"]
        else:
            new = None
            for salt in range(TRIES):
                cand = derive_card(c, salt)
                if not exclusions.hit(cand, banned):
                    new = cand
                    break
            if new is None:
                held["excluded"] += 1
                held_ids.append(c["id"])
                continue
            if leaks(c, new):
                held["real-word"] += 1
                held_ids.append(c["id"])
                review.append(f"| {c['id']} | HELD: real word kept | {c['text']} | {new} |")
                continue
            review.append(f"| {c['id']} | | {c['text']} | {new} |")
        shipped.append({**{k: c[k] for k in ("id", "spans", "alternatives", "doubtful", "flag")}, "text": new})
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / f"round-{n}.jsonl").open("w") as f:
        for c in shipped:
            keys = ("id", "text", "spans", "alternatives", "doubtful", "flag")
            f.write(json.dumps({k: c[k] for k in keys}, ensure_ascii=False) + "\n")
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / f"round-{n}.md").write_text(
        f"# Round {n}: labeled text and shipped text (private)\n\n| id | note | labeled | shipped |\n|---|---|---|---|\n"
        + "\n".join(review)
        + "\n",
        encoding="utf-8",
    )
    return {"round": n, "cards": len(cards), "shipped": len(shipped), "held": dict(held), "held_ids": held_ids}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rounds", nargs="+", type=int)
    ap.add_argument("--private-root", type=Path, default=None, help="doorplate checkout (exclusion corpora)")
    a = ap.parse_args()
    try:
        banned, _ = sample.exclusion_set(a.private_root or sample.DEFAULT_PRIVATE)
    except Exception as e:  # noqa: BLE001  (corpus readers can quote rows)
        raise SystemExit(f"exclusion corpora: {type(e).__name__}") from None
    prov = {p["id"]: p for p in map(json.loads, (ROOT / "sets/golden/provenance.jsonl").read_text().splitlines())}
    for n in a.rounds:
        res = derive_round(n, banned, store.GOLD_DIR, store.SHIPPED_GOLD_DIR, store.GOLD_DIR.parent / "review", prov)
        print(json.dumps(res))


if __name__ == "__main__":
    main()
