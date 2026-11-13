"""Blind labeling storage: cards, spans, the append-only label log, and the gold export.

Nothing in this module (or in `server.py`) imports an adapter or reads a parser's output: that is what keeps labeling
blind. Only `adjudicate.py` runs parsers, and only after a round is fully labeled.

A card's spans are `[start, end, label]` over the card text, with canonical *leaf* labels (the fine part where a field
has fine parts, the coarse label otherwise). Text with no span is unlabeled. `alternatives` lists extra readings the
gold accepts for a span: `{"start", "end", "labels": [...]}` (the conventions in `schema/conventions.toml`, per card).
"""

import json
import time
from pathlib import Path

from schema import labels

ROOT = Path(__file__).resolve().parents[2]
ROUNDS = ROOT / "sets" / "golden" / "rounds"
LOG_DIR = ROOT / "local-data" / "labels"
GOLD_DIR = ROOT / "sets" / "golden" / "gold"

KEYS = "1234567890qwertyuiopasdfgh"
# The most used labels get the first keys; the rest follow in schema order.
COMMON = [
    "house_number_value", "street_pre_direction", "street_name", "street_post_type", "street_post_direction",
    "unit_type", "unit_value", "city", "state", "postal_code",
]  # fmt: skip


def leaf_labels() -> list[str]:
    """The labels a span can carry: every label with no fine parts."""
    all_ = labels()
    parents = {lab.parent for lab in all_.values() if lab.parent}
    return [name for name in all_ if name not in parents]


def key_map() -> dict[str, str]:
    """Hot key to label, in schema order."""
    leaves = leaf_labels()
    leaves = [x for x in COMMON if x in leaves] + [x for x in leaves if x not in COMMON]
    assert len(leaves) <= len(KEYS)
    return dict(zip(KEYS, leaves, strict=False))


FLAGS = ("non_address", "ambiguous")  # a card with no right reading (COMPOSITION.md, "Difficulty tiers")


class CardError(ValueError):
    """A card that cannot be saved. Messages never quote the text."""


def check_spans(text: str, spans: list, *, what: str = "span") -> list[list]:
    """Validate spans (in range, ordered, not overlapping, known leaf labels) and return them sorted."""
    leaves = set(leaf_labels())
    out = []
    for sp in spans:
        if not (isinstance(sp, list | tuple) and len(sp) == 3):
            raise CardError(f"{what} must be [start, end, label]")
        s, e, lab = sp
        if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(text)):
            raise CardError(f"{what} out of range")
        if lab not in leaves:
            raise CardError(f"unknown label {lab!r}")
        if text[s:e] != text[s:e].strip():
            raise CardError(f"{what} starts or ends with a space")
        out.append([s, e, lab])
    out.sort()
    for a, b in zip(out, out[1:], strict=False):
        if a[1] > b[0]:
            raise CardError(f"{what}s overlap")
    return out


def check_alternatives(text: str, alts: list) -> list[dict]:
    leaves = set(leaf_labels()) | {"none"}  # `none`: the span may also be left unlabeled (the `#` convention)
    out = []
    for alt in alts:
        s, e, labs = alt.get("start"), alt.get("end"), alt.get("labels")
        if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(text)):
            raise CardError("alternative out of range")
        if not (isinstance(labs, list) and labs and all(lab in leaves for lab in labs)):
            raise CardError("alternative needs known labels")
        out.append({"start": s, "end": e, "labels": sorted(set(labs))})
    return out


def check_flag(flag) -> str | None:
    """`non_address` (gold: no fields), `ambiguous` (every accepted reading listed as alternatives) or none."""
    if flag in (None, ""):
        return None
    if flag not in FLAGS:
        raise CardError("unknown flag")
    return flag


def load_round(n: int, rounds_dir: Path = ROUNDS) -> list[dict]:
    """The unlabeled records of round `n` (`{id, text}`)."""
    path = rounds_dir / f"round-{n}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def log_path(n: int, log_dir: Path = LOG_DIR) -> Path:
    return log_dir / f"round-{n}.jsonl"


def load_log(n: int, log_dir: Path = LOG_DIR) -> dict[str, dict]:
    """The latest saved record per card id (the log keeps every save, for the timings and the history)."""
    path = log_path(n, log_dir)
    latest: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                latest[rec["id"]] = rec
    return latest


def save_card(n: int, card: dict, payload: dict, *, phase: str = "label", log_dir: Path = LOG_DIR) -> dict:
    """Validate and append one card's labels. `phase` is "label" (blind pass) or "adjudicate"."""
    text = card["text"]
    spans = check_spans(text, payload.get("spans", []))
    rec = {
        "id": card["id"],
        "phase": phase,
        "spans": spans,
        "alternatives": check_alternatives(text, payload.get("alternatives", [])),
        "doubtful": bool(payload.get("doubtful", False)),
        "flag": check_flag(payload.get("flag")),
        "ms": max(0, int(payload.get("ms", 0))),
        "keys": max(0, int(payload.get("keys", 0))),
        "ts": int(time.time()),
    }
    log_dir.mkdir(parents=True, exist_ok=True)
    with log_path(n, log_dir).open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def gold_cards(n: int, rounds_dir: Path = ROUNDS, log_dir: Path = LOG_DIR) -> list[dict]:
    """Records of round `n` with their latest labels (unlabeled records have `labeled: false`)."""
    saved = load_log(n, log_dir)
    out = []
    for rec in load_round(n, rounds_dir):
        got = saved.get(rec["id"])
        out.append(
            {**rec, "labeled": got is not None}
            | ({k: got.get(k) for k in ("spans", "alternatives", "doubtful", "flag", "phase")} if got else {})
        )
    return out


def export_round(n: int, gold_dir: Path = GOLD_DIR, rounds_dir: Path = ROUNDS, log_dir: Path = LOG_DIR) -> dict:
    """Write the committed gold file of a fully labeled round and return its counts."""
    cards = gold_cards(n, rounds_dir, log_dir)
    missing = sum(not c["labeled"] for c in cards)
    if missing:
        raise CardError(f"round {n}: {missing} of {len(cards)} cards are not labeled")
    gold_dir.mkdir(parents=True, exist_ok=True)
    with (gold_dir / f"round-{n}.jsonl").open("w") as f:
        keys = ("id", "text", "spans", "alternatives", "doubtful", "flag")
        for c in cards:
            f.write(json.dumps({k: c[k] for k in keys}, ensure_ascii=False) + "\n")
    saved = load_log(n, log_dir)
    changed = sum(1 for c in cards if saved[c["id"]]["phase"] == "adjudicate")
    return {
        "round": n,
        "cards": len(cards),
        "doubtful": sum(c["doubtful"] for c in cards),
        "flagged": sum(bool(c["flag"]) for c in cards),
        "with_alternatives": sum(bool(c["alternatives"]) for c in cards),
        "adjudicated_saves": changed,
    }
