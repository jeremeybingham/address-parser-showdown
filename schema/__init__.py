"""The canonical label schema, loaded from `schema.toml`."""

import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.toml")


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
