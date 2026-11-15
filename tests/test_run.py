"""The run entry point's guards (no parser is run)."""

import pytest

from tools import run


def test_existing_run_folder_is_never_overwritten(tmp_path, monkeypatch):
    (tmp_path / "2026-01-01").mkdir()
    monkeypatch.setattr(run, "RUNS", tmp_path)
    with pytest.raises(SystemExit, match="never overwritten"):
        run.prepare("2026-01-01", allow_dirty=True)


def test_dirty_tree_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "RUNS", tmp_path)
    monkeypatch.setattr(run, "clean_tree", lambda: False)
    with pytest.raises(SystemExit, match="not clean"):
        run.prepare("2026-01-02", allow_dirty=False)
    assert run.prepare("2026-01-02", allow_dirty=True) == tmp_path / "2026-01-02"
