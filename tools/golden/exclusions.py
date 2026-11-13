"""The exclusion string check: nothing in the golden set may appear in any corpus a parser was built or tested on.

The corpora (doorplate's, the benchmark suite, usaddress's training files, libpostal's test files, the geocode
benchmark) are read from a checkout beside this one; `load` returns a set of normalized strings. A candidate is
rejected when its whole text or its first line (the street line) matches one of them. Normalization: lowercase,
letters and digits only, so case, commas and spacing never hide a copy.
"""

from __future__ import annotations

import gzip
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

MIN_LEN = 8  # shorter normalized strings ("po box 1") would match by accident


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def _jsonl(path: Path):
    op = gzip.open if path.suffix == ".gz" else open
    with op(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            yield from _strings(rec)
            fields = rec.get("fields") if isinstance(rec, dict) else None
            if isinstance(fields, dict):  # doorplate's corpus: the lines joined, as a parser would see them
                yield ", ".join(str(v) for v in fields.values() if v)


def _xml(path: Path):
    for el in ET.parse(path).getroot().iter("AddressString"):
        yield " ".join("".join(el.itertext()).split())


def _conll(path: Path):
    """Token-per-line files (word LABEL), records separated by `-END-` or a blank line."""
    words: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts or parts[0] == "-END-":
            if words:
                yield " ".join(words)
            words = []
        else:
            words.append(parts[0])
    if words:
        yield " ".join(words)


def _c_strings(path: Path):
    yield from re.findall(r'"((?:[^"\\]|\\.)*)"', path.read_text(encoding="utf-8", errors="replace"))


READERS = {".jsonl": _jsonl, ".gz": _jsonl, ".xml": _xml, ".txt": _conll, ".c": _c_strings}


def load(paths: list[Path]) -> tuple[set[str], dict[str, int]]:
    """Normalized strings from every readable file under `paths`; counts per path given."""
    seen: set[str] = set()
    counts: dict[str, int] = {}
    for root in paths:
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.suffix in READERS)
        n = 0
        for f in files:
            try:
                for s in READERS[f.suffix](f):
                    k = norm(s)
                    if len(k) >= MIN_LEN:
                        seen.add(k)
                        n += 1
            except Exception as e:  # a corpus line may hold a private row; print only the type
                counts[f"{root}:{f.name}:{type(e).__name__}"] = 0
        counts[str(root)] = n
    return seen, counts


def hit(text: str, banned: set[str]) -> bool:
    first = norm(text.split(",")[0])
    return norm(text) in banned or (len(first) >= MIN_LEN and first in banned)
