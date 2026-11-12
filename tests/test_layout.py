"""The repository layout that the docs and the plan rely on."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_layout_folders_have_readmes():
    for folder in ("schema", "adapters", "sets", "scorer", "runs", "report"):
        assert (ROOT / folder / "README.md").is_file(), folder


def test_methodology_exists():
    assert (ROOT / "METHODOLOGY.md").is_file()
