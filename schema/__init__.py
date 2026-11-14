"""The canonical label schema, loaded from `schema.toml`."""

import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.toml")

# What a golden card's text is, when it is not one door (METHODOLOGY.md, "How the golden set is labeled"). A card with
# no flag is one door. A flagged card keeps its spans and is reported on its own line, in no tier figure or score.
FLAGS = (
    "non_address",  # not an address: no spans
    "ambiguous",  # one door, several readings: one reading labeled, the others as alternatives
    "multi_address",  # two or more doors (`12 & 14 Oak St`, `12 Oak St & 3 Elm Ave`): every part as written
    "intersection",  # a corner (`Oak St & Elm Ave`): no door; the streets and the last line labeled
)


@dataclass(frozen=True)
class Label:
    name: str
    scope: str  # "core", "out_of_scope" or "unscored"
    parent: str | None
    doc: str


@cache
def labels() -> dict[str, Label]:
    """Every canonical label by name, in file order."""
    raw = tomllib.loads(SCHEMA_PATH.read_text())["label"]
    out = {r["name"]: Label(r["name"], r["scope"], r.get("parent"), r["doc"]) for r in raw}
    for lab in out.values():
        if lab.parent is not None and (lab.parent not in out or out[lab.parent].parent):
            raise ValueError(f"label {lab.name}: parent must be a coarse label")
    return out


def coarse(label: str) -> str:
    """The coarse field a label belongs to (a coarse label is its own)."""
    lab = labels()[label]
    return lab.parent or lab.name


def fine_parts(field: str) -> list[str]:
    """The fine labels of a coarse field (empty when it has none)."""
    return [lab.name for lab in labels().values() if lab.parent == field]


CONVENTIONS_PATH = Path(__file__).with_name("conventions.toml")


@cache
def conventions() -> dict[str, dict]:
    """The accepted-reading conventions by id. Readings are canonical labels, or `none` (the span is left unlabeled)."""
    out = {}
    for c in tomllib.loads(CONVENTIONS_PATH.read_text()).get("convention", []):
        known = set(labels()) | {"none"}
        if not (c.get("source") and c.get("question") and set(c["readings"]) <= known and len(c["readings"]) >= 2):
            raise ValueError(f"convention {c.get('id')}: needs a source, a question and known readings (two or more)")
        out[c["id"]] = c
    return out
