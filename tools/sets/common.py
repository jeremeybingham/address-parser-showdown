"""The record format every converted set shares, and where converted sets and predictions go.

A record is `{"id", "text", "spans", "part"}` plus whatever the source carries that a report may slice by. `spans` are
`[start, end, label]` over `text` with canonical labels, the golden set's format (`tools/label/store.py`), except that a
coarse label is allowed where the source labels a field without its fine parts (usaddress's `StreetNamePreModifier`
is `street`): that span is scored on the coarse track only.
`part` names the piece of the set a figure is reported on (a stratum, a split), and each set's `PARTS` says which parts
are home sets for a parser.

Converted sets and prediction files are written under `build/` (git-ignored): every converter is deterministic, and
the set's `MANIFEST.md` holds the SHA-256 of its output, so a rerun proves it produced the same file.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from adapters.base import Mapping, Span, align
from schema import labels

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SETS_OUT = BUILD / "sets"
PREDICTIONS = BUILD / "predictions"
SEPARATORS = ",;"


class SpanError(ValueError):
    """Gold spans that do not fit the text (the message never quotes it)."""


class SourceError(RuntimeError):
    """A source file is missing or is not the pinned one."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sha(path: Path, want: str) -> None:
    if not path.is_file():
        raise SourceError(f"missing source file {path}")
    got = sha256(path)
    if got != want:
        raise SourceError(f"{path.name}: SHA-256 {got}, pinned {want}")


def merge_adjacent(text: str, spans: list[Span]) -> list[Span]:
    """Join neighbouring spans with the same label when only spaces lie between them (`PELL` + `CITY`).

    A comma or semicolon between them keeps them apart. This is how a person labels: one span per field part.
    """
    out: list[Span] = []
    for s in spans:
        if out and out[-1].label == s.label and not text[out[-1].end : s.start].strip():
            out[-1] = Span(out[-1].start, s.end, s.label)
        else:
            out.append(s)
    return out


def check_spans(text: str, spans: list[list]) -> list[list]:
    """In range, no space at either end, known labels, sorted, not overlapping; returns them sorted."""
    known = labels()
    out = sorted(spans)
    for s, e, lab in out:
        if not (0 <= s < e <= len(text)) or text[s:e] != text[s:e].strip():
            raise SpanError("span out of range or with a space at an end")
        if lab not in known:
            raise SpanError(f"unknown label {lab!r}")
    if any(a[1] > b[0] for a, b in zip(out, out[1:], strict=False)):
        raise SpanError("spans overlap")
    return out


def tokens_to_spans(text: str, tokens: list[tuple[str, str]], mapping: Mapping) -> list[list]:
    """Gold `(token, native label)` pairs to checked canonical leaf spans."""
    spans = mapping.to_canonical(align(text, tokens))
    return check_spans(text, [[s.start, s.end, s.label] for s in merge_adjacent(text, spans)])


def write_jsonl(path: Path, records) -> int:
    """Write records (sorted keys; gzip with no name and a fixed time, so the bytes repeat); return the count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
        for r in records:
            gz.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n").encode())
            n += 1
    return n


def read_jsonl(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def set_path(name: str) -> Path:
    return SETS_OUT / f"{name}.jsonl.gz"


def components_to_spans(text: str, comps: list[tuple[str, str]], mapping: Mapping) -> list[list]:
    """Gold `(native label, value)` components of libpostal's kind (lowercased, free of commas) to checked spans.

    Each value is found in `text`, ignoring case, after the previous one; a value that is not there raises
    `AlignmentError` and the record is dropped and counted by the caller.
    """
    spans = mapping.to_canonical(align(text, [(v, lab) for lab, v in comps], ignore_case=True))
    return check_spans(text, [[s.start, s.end, s.label] for s in merge_adjacent(text, spans)])
