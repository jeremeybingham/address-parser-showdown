"""The conformance check every adapter must pass (run by `tests/test_conformance.py`; see `adapters/README.md`).

An adapter conforms when, for every string in `conformance_strings.txt`:

- its spans are in order, inside the string, non-empty and not overlapping;
- every label is one the mapping knows, and the mapping sends every label to a canonical label;
- for the `cover` strings, every letter and digit of the string is inside a span.

Problems are described by string number and kind only, never by quoting the string (the same check may later run on
private data).
"""

from pathlib import Path

from adapters.base import Adapter
from schema import labels as schema_labels

STRINGS = Path(__file__).with_name("conformance_strings.txt")


def load_strings() -> list[tuple[str, str]]:
    """`(kind, string)` pairs. A string is kept exactly as written, spaces included."""
    out = []
    for line in STRINGS.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            kind, text = line.split("|", 1)
            out.append((kind, text))
    return out


def mapping_problems(adapter: Adapter) -> list[str]:
    known = schema_labels()
    problems = []
    for native, rule in adapter.mapping.rules.items():
        for target in (rule["default"], rule.get("then")):
            if target is not None and target not in known:
                problems.append(f"{native}: unknown canonical label {target}")
    return problems


def check(adapter: Adapter) -> list[str]:
    """Every problem found, as short descriptions; an empty list means the adapter conforms."""
    problems = mapping_problems(adapter)
    cases = load_strings()
    results = adapter.parse_many([text for _, text in cases])
    for number, ((kind, text), spans) in enumerate(zip(cases, results, strict=True), start=1):
        where = f"string {number} ({kind})"
        end_before = 0
        for s in spans:
            if not (0 <= s.start < s.end <= len(text)):
                problems.append(f"{where}: span out of bounds")
            elif s.start < end_before:
                problems.append(f"{where}: spans overlap or are out of order")
            else:
                end_before = s.end
            if s.label not in adapter.mapping.rules:
                problems.append(f"{where}: label not in the mapping")
        if kind == "cover":
            covered = {i for s in spans for i in range(s.start, s.end)}
            missing = [i for i, ch in enumerate(text) if ch.isalnum() and i not in covered]
            if missing:
                problems.append(f"{where}: {len(missing)} letters or digits outside every span")
        try:
            adapter.mapping.to_canonical(spans)
        except KeyError:
            problems.append(f"{where}: label cannot be mapped")
    return problems
