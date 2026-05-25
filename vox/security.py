"""Dangerous command detection."""

from __future__ import annotations

import re

# Each entry: (compiled regex, human-readable reason)
_DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\brm\s+.*-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/\s*$"), "Recursive force-delete on root filesystem"),
    (re.compile(r"\brm\s+.*-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+/\s*$"), "Recursive force-delete on root filesystem"),
    (re.compile(r"\brm\s+.*-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/[a-z]*\s*$"), "Recursive force-delete on system directory"),
    (re.compile(r"\bmkfs\b"), "Filesystem formatting — will destroy data"),
    (re.compile(r"\bdd\s+if="), "Raw disk write — can destroy partitions"),
    (re.compile(r"\bshutdown\b"), "System shutdown"),
    (re.compile(r"\breboot\b"), "System reboot"),
    (re.compile(r"\binit\s+[06]\b"), "System halt/reboot via init"),
    (re.compile(r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;?\s*:"), "Fork bomb"),
    (re.compile(r">\s*/dev/sd[a-z]"), "Direct write to block device"),
    (re.compile(r"\bchmod\s+.*777\s+/"), "Dangerous permission change on system path"),
    (re.compile(r"\bchown\s+.*\s+/\s*$"), "Ownership change on root filesystem"),
    (re.compile(r"\bwget\b.*\|\s*(ba)?sh"), "Piping remote script to shell"),
    (re.compile(r"\bcurl\b.*\|\s*(ba)?sh"), "Piping remote script to shell"),
    (re.compile(r"\b:(){ :\|:& };:"), "Fork bomb (alternate form)"),
    (re.compile(r">\s*/dev/null\s+2>&1\s*&\s*disown"), "Stealth background process"),
]


def check_command(cmd: str) -> tuple[bool, str]:
    """Check if a command matches any dangerous pattern.

    Returns:
        (is_dangerous, reason) — reason is empty string if safe.
    """
    stripped = cmd.strip()
    for pattern, reason in _DANGEROUS_PATTERNS:
        if pattern.search(stripped):
            return True, reason
    return False, ""
