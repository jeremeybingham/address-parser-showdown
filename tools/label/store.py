"""Blind labeling storage: cards, spans, the append-only label log, and the gold export.

Nothing in this module (or in `server.py`) imports an adapter or reads a parser's output: that is what keeps labeling
blind. Only `adjudicate.py` runs parsers, and only after a round is fully labeled.

A card's spans are `[start, end, label]` over the card text, with canonical *leaf* labels (the fine part where a field
has fine parts, the coarse label otherwise). Text with no span is unlabeled. `alternatives` lists extra readings the
gold accepts for a span: `{"start", "end", "labels": [...]}` (the conventions in `schema/conventions.toml`, per card).

Labeling is done on the unmasked text (`local-data/golden-real/rounds/`, written by `tools/golden/sample.py --real`),
so a hard card can be looked up on a map. The gold export stays in `local-data/golden-real/gold/`; only
`tools/golden/derive.py` writes the shipped gold, with invented values in place of the private ones.

Besides the spans, a card records what its text is (`flag`, `schema.FLAGS`; none = one door), how sure the labeler is
(`doubtful`, or `rough`: only the clear parts are labeled), `unscored` regions (`[start, end]`: text left out of the
score on both sides, for a stretch no reading can be defended), and a private `note` and `revisit` mark. Notes and
revisit marks stay in the log: the export and the shipped gold never carry them.
"""

import hashlib
import json
import time
from pathlib import Path

from schema import FLAGS, labels

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROUNDS = ROOT / "sets" / "golden" / "rounds"  # the anonymized draw (committed)
ROUNDS = ROOT / "local-data" / "golden-real" / "rounds"  # the same cards unmasked: what is labeled (git-ignored)
LOG_DIR = ROOT / "local-data" / "labels"
GOLD_DIR = ROOT / "local-data" / "golden-real" / "gold"  # private gold on the unmasked text
SHIPPED_GOLD_DIR = ROOT / "sets" / "golden" / "gold"  # written by tools/golden/derive.py only

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


NOTE_MAX = 500  # characters in a card's private note
SURENESS_FIELDS = ("flag", "doubtful", "rough", "unscored")  # what takes a card out of the headline (`late_changes`)


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


def check_unscored(text: str, regions: list, spans: list[list]) -> list[list]:
    """Validate unscored regions (in range, no edge space, not overlapping each other or a span); return them sorted."""
    out = []
    for r in regions:
        if not (isinstance(r, list | tuple) and len(r) == 2):
            raise CardError("unscored region must be [start, end]")
        s, e = r
        if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(text)):
            raise CardError("unscored region out of range")
        if text[s:e] != text[s:e].strip():
            raise CardError("unscored region starts or ends with a space")
        out.append([s, e])
    out.sort()
    for a, b in zip(out, out[1:], strict=False):
        if a[1] > b[0]:
            raise CardError("unscored regions overlap")
    if any(s < r_end and r_start < e for s, e, _ in spans for r_start, r_end in out):
        raise CardError("a span overlaps an unscored region")
    return out


def check_flag(flag) -> str | None:
    """What the text is when it is not one door (`schema.FLAGS`), or none."""
    if flag in (None, ""):
        return None
    if flag not in FLAGS:
        raise CardError("unknown flag")
    return flag


def load_round(n: int, rounds_dir: Path = ROUNDS) -> list[dict]:
    """The unlabeled records of round `n` (`{id, text}`)."""
    path = rounds_dir / f"round-{n}.jsonl"
    if not path.exists():
        raise SystemExit(f"{path} is missing; run `uv run python tools/golden/sample.py --confirm --real` first")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def text_hash(text: str) -> str:
    """Stamped on every save: a save counts only for the text it was made on."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


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
                if rec.get("void"):  # a re-queue: the card is unlabeled again (earlier saves stay in the log)
                    latest.pop(rec["id"], None)
                else:
                    latest[rec["id"]] = rec
    return latest


def requeue(n: int, ids: list[str], log_dir: Path = LOG_DIR) -> None:
    """Mark cards of round `n` as unlabeled again by appending a void record for each (the log is never rewritten)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    with log_path(n, log_dir).open("a") as f:
        for cid in ids:
            f.write(json.dumps({"id": cid, "void": True, "ts": int(time.time())}) + "\n")


def save_card(n: int, card: dict, payload: dict, *, phase: str = "label", log_dir: Path = LOG_DIR) -> dict:
    """Validate and append one card's labels. `phase` is "label" (blind pass) or "adjudicate"."""
    text = card["text"]
    spans = check_spans(text, payload.get("spans", []))
    doubtful, rough = bool(payload.get("doubtful", False)), bool(payload.get("rough", False))
    if doubtful and rough:
        raise CardError("a card is doubtful or rough, not both")
    note = payload.get("note") or ""
    if not isinstance(note, str) or len(note) > NOTE_MAX:
        raise CardError(f"note must be text of at most {NOTE_MAX} characters")
    rec = {
        "id": card["id"],
        "phase": phase,
        "spans": spans,
        "alternatives": check_alternatives(text, payload.get("alternatives", [])),
        "doubtful": doubtful,
        "rough": rough,
        "unscored": check_unscored(text, payload.get("unscored", []), spans),
        "flag": check_flag(payload.get("flag")),
        "note": note.strip(),
        "revisit": bool(payload.get("revisit", False)),
        "ms": max(0, int(payload.get("ms", 0))),
        "keys": max(0, int(payload.get("keys", 0))),
        "ts": int(time.time()),
        "th": text_hash(text),
    }
    log_dir.mkdir(parents=True, exist_ok=True)
    with log_path(n, log_dir).open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


CARD_FIELDS = {  # saved fields served to the page, with the default for saves made before the field existed
    "spans": [],
    "alternatives": [],
    "doubtful": False,
    "rough": False,
    "unscored": [],
    "flag": None,
    "note": "",
    "revisit": False,
    "phase": "label",
}
EXPORT_KEYS = ("id", "text", "spans", "alternatives", "doubtful", "rough", "unscored", "flag")  # never note or revisit


def gold_cards(
    n: int, rounds_dir: Path = ROUNDS, log_dir: Path = LOG_DIR, legacy_dir: Path = PUBLIC_ROUNDS
) -> list[dict]:
    """Records of round `n` with their latest labels (unlabeled records have `labeled: false`).

    A save made on other text (the anonymized text, before labeling moved to the unmasked text) does not count: the card
    is unlabeled again and `stale: true`. Saves from before the text stamp were made on the round in `legacy_dir`.
    """
    saved = load_log(n, log_dir)
    legacy_path = legacy_dir / f"round-{n}.jsonl"
    legacy = {r["id"]: text_hash(r["text"]) for r in load_round(n, legacy_dir)} if legacy_path.exists() else {}
    out = []
    for rec in load_round(n, rounds_dir):
        got = saved.get(rec["id"])
        stale = got is not None and got.get("th", legacy.get(rec["id"])) != text_hash(rec["text"])
        if stale:
            got = None
        out.append(
            {**rec, "labeled": got is not None, "stale": stale}
            | ({k: got.get(k, d) for k, d in CARD_FIELDS.items()} if got else {})
        )
    return out


def export_round(n: int, gold_dir: Path = GOLD_DIR, rounds_dir: Path = ROUNDS, log_dir: Path = LOG_DIR) -> dict:
    """Write the committed gold file of a fully labeled round and return its counts."""
    cards = gold_cards(n, rounds_dir, log_dir, legacy_dir=rounds_dir)
    missing = sum(not c["labeled"] for c in cards)
    if missing:
        raise CardError(f"round {n}: {missing} of {len(cards)} cards are not labeled")
    gold_dir.mkdir(parents=True, exist_ok=True)
    with (gold_dir / f"round-{n}.jsonl").open("w") as f:
        for c in cards:
            f.write(json.dumps({k: c[k] for k in EXPORT_KEYS}, ensure_ascii=False) + "\n")
    changed = sum(1 for c in cards if c["phase"] == "adjudicate")
    return {
        "round": n,
        "cards": len(cards),
        "doubtful": sum(c["doubtful"] for c in cards),
        "rough": sum(c["rough"] for c in cards),
        "with_unscored": sum(bool(c["unscored"]) for c in cards),
        "flagged": sum(bool(c["flag"]) for c in cards),
        "revisit_open": sum(c["revisit"] for c in cards),
        "late_changes": len(late_changes(n, log_dir)),
        "with_alternatives": sum(bool(c["alternatives"]) for c in cards),
        "adjudicated_saves": changed,
    }


def late_changes(n: int, log_dir: Path = LOG_DIR) -> list[str]:
    """Cards of round `n` whose flag, sureness or unscored regions changed in adjudication (after the parsers ran).

    Only a blind mark may take a card out of the headline; a change made after seeing parser output is counted and
    listed in the report (METHODOLOGY.md). Compares each card's latest save from its first adjudication save on with its
    latest save before that.
    """
    path = log_path(n, log_dir)
    before: dict[str, tuple] = {}
    after: dict[str, tuple] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("void"):
                before.pop(rec["id"], None)
                after.pop(rec["id"], None)
                continue
            key = tuple(json.dumps(rec.get(k, CARD_FIELDS[k])) for k in SURENESS_FIELDS)
            if rec.get("phase") == "adjudicate" or rec["id"] in after:  # any save after adjudication began
                after[rec["id"]] = key
            else:
                before[rec["id"]] = key
    return sorted(cid for cid, key in after.items() if before.get(cid) != key)
