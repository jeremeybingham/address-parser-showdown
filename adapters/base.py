"""The adapter contract: a string in, character spans in the parser's own labels out, and a mapping to the schema."""

import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from schema import labels as schema_labels

MAPPINGS = Path(__file__).with_name("mappings")
SEPARATORS = ",;"  # trimmed from the ends of a span; periods and other marks stay


@dataclass(frozen=True)
class Span:
    """Characters `text[start:end]` carry the parser's label `label`."""

    start: int
    end: int
    label: str


class AlignmentError(ValueError):
    """A token the parser returned could not be found in the input (the message never quotes the input)."""


def align(text: str, pieces: list[tuple[str, str | None]], *, ignore_case: bool = False) -> list[Span]:
    """Place `(token, label)` pieces in `text`, in order, as character spans.

    A piece with label None is skipped. A piece of several words (libpostal's) spans from its first word to its last.
    `,;` at the ends of a word are not part of the span.
    """
    hay = text.lower() if ignore_case else text
    cursor = 0
    spans = []
    for token, label in pieces:
        first = last = None
        for word in token.split():
            word = word.strip(SEPARATORS)
            if not word:
                continue
            start = hay.find(word.lower() if ignore_case else word, cursor)
            if start < 0:
                raise AlignmentError(f"token of length {len(word)} not found after offset {cursor}")
            cursor = start + len(word)
            first = start if first is None else first
            last = cursor
        if label is not None and first is not None:
            spans.append(Span(first, last, label))
    return spans


class Mapping:
    """A parser's labels to canonical labels, from `adapters/mappings/<name>.toml`."""

    def __init__(self, name: str):
        raw = tomllib.loads((MAPPINGS / f"{name}.toml").read_text())["labels"]
        known = schema_labels()
        self.rules: dict[str, dict] = {}
        for native, rule in raw.items():
            rule = {"default": rule} if isinstance(rule, str) else dict(rule)
            for target in (rule["default"], rule.get("then")):
                if target is not None and target not in known:
                    raise ValueError(f"mapping {name}: {native} maps to unknown label {target}")
            self.rules[native] = rule

    @property
    def native_labels(self) -> set[str]:
        return set(self.rules)

    @property
    def claims(self) -> set[str]:
        """The canonical labels this parser can produce (`other` excluded)."""
        out = set()
        for rule in self.rules.values():
            out.update(t for t in (rule["default"], rule.get("then")) if t and t != "other")
        return out

    def to_canonical(self, spans: list[Span]) -> list[Span]:
        """The spans with canonical labels. Raises KeyError for a label the mapping does not have."""
        present = {s.label for s in spans}
        out = []
        for s in spans:
            rule = self.rules[s.label]
            hit = rule.get("if_string_has") and present & set(rule["if_string_has"])
            out.append(Span(s.start, s.end, rule["then"] if hit else rule["default"]))
        return out


class Adapter(ABC):
    """One parser. A subclass sets `name`, loads its `mapping`, and implements `parse` and `versions`."""

    name: str
    mapping: Mapping

    @abstractmethod
    def parse(self, text: str) -> list[Span]:
        """Spans in the parser's own labels, in order, not overlapping. Text the parser leaves unlabeled has no span."""

    def parse_many(self, texts: list[str]) -> list[list[Span]]:
        return [self.parse(t) for t in texts]

    @abstractmethod
    def versions(self) -> dict[str, str]:
        """What a figure must name: the version (and model checksum) of the parser that produced it."""

    def canonical(self, text: str) -> list[Span]:
        return self.mapping.to_canonical(self.parse(text))
