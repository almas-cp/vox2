"""Tests for vox.history — JSON-backed command history."""

import json
from pathlib import Path

import pytest

from vox import history


@pytest.fixture(autouse=True)
def tmp_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect history file to a temp location."""
    hist_file = tmp_path / "vox_history.json"
    monkeypatch.setattr(history, "HISTORY_FILE", hist_file)
    return hist_file


def test_add_and_get() -> None:
    history.add_entry("list files", "ls -la")
    history.add_entry("disk usage", "du -sh *")

    entries = history.get_all()
    assert len(entries) == 2
    # Newest first
    assert entries[0]["query"] == "disk usage"
    assert entries[1]["query"] == "list files"


def test_search() -> None:
    history.add_entry("find python files", "find . -name '*.py'")
    history.add_entry("list all files", "ls -la")
    history.add_entry("compress folder", "tar czf out.tar.gz .")

    results = history.search("files")
    assert len(results) == 2
    queries = {r["query"] for r in results}
    assert "find python files" in queries
    assert "list all files" in queries


def test_search_case_insensitive() -> None:
    history.add_entry("Docker PS", "docker ps")
    results = history.search("docker")
    assert len(results) == 1


def test_toggle_favorite() -> None:
    history.add_entry("test", "echo test")
    # Index 0 = newest
    new_state = history.toggle_favorite(0)
    assert new_state is True

    entries = history.get_all()
    assert entries[0]["favorite"] is True

    # Toggle back
    new_state = history.toggle_favorite(0)
    assert new_state is False


def test_pruning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(history, "MAX_ENTRIES", 5)

    for i in range(10):
        history.add_entry(f"query {i}", f"cmd {i}")

    entries = history.get_all()
    assert len(entries) == 5
    # Should keep the last 5 (newest)
    assert entries[0]["query"] == "query 9"
    assert entries[4]["query"] == "query 5"


def test_get_entry() -> None:
    history.add_entry("first", "cmd1")
    history.add_entry("second", "cmd2")

    entry = history.get_entry(0)
    assert entry is not None
    assert entry["query"] == "second"

    entry = history.get_entry(1)
    assert entry is not None
    assert entry["query"] == "first"

    assert history.get_entry(99) is None


def test_corrupted_file(tmp_history: Path) -> None:
    tmp_history.write_text("not valid json{{{", encoding="utf-8")
    entries = history.get_all()
    assert entries == []
