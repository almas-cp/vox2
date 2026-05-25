"""Clipboard support with graceful fallback."""

from __future__ import annotations


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard.

    Returns True on success, False if clipboard is unavailable.
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False
