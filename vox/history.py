"""Persistent command history stored in ~/.vox_history.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HISTORY_FILE = Path.home() / ".vox_history.json"
MAX_ENTRIES = 500


def _load() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: list[dict[str, Any]]) -> None:
    # Prune to MAX_ENTRIES before saving
    trimmed = entries[-MAX_ENTRIES:]
    HISTORY_FILE.write_text(json.dumps(trimmed, indent=2, ensure_ascii=False), encoding="utf-8")


def add_entry(query: str, command: str) -> None:
    """Append a new history entry."""
    entries = _load()
    entries.append({
        "query": query,
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "favorite": False,
    })
    _save(entries)


def get_all() -> list[dict[str, Any]]:
    """Return all history entries, newest first."""
    return list(reversed(_load()))


def search(term: str) -> list[dict[str, Any]]:
    """Search history by query or command substring (case-insensitive)."""
    term_lower = term.lower()
    return [
        e for e in get_all()
        if term_lower in e.get("query", "").lower()
        or term_lower in e.get("command", "").lower()
    ]


def toggle_favorite(index: int) -> bool:
    """Toggle the favorite flag on entry at `index` (0 = newest). Returns new state."""
    entries = _load()
    reversed_idx = len(entries) - 1 - index
    if 0 <= reversed_idx < len(entries):
        entries[reversed_idx]["favorite"] = not entries[reversed_idx].get("favorite", False)
        _save(entries)
        return entries[reversed_idx]["favorite"]
    return False


def get_entry(index: int) -> dict[str, Any] | None:
    """Get a single entry by index (0 = newest)."""
    all_entries = get_all()
    if 0 <= index < len(all_entries):
        return all_entries[index]
    return None
