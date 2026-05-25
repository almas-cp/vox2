"""System utilities: shell and distro detection."""

from __future__ import annotations

import os
import platform
from pathlib import Path


def detect_shell() -> str:
    """Return the current shell name (bash, zsh, fish, etc.)."""
    shell = os.environ.get("SHELL", "")
    if shell:
        return Path(shell).name
    # Fallback for non-POSIX
    return os.environ.get("COMSPEC", "sh").rsplit("\\", 1)[-1].rsplit("/", 1)[-1]


def detect_distro() -> str:
    """Return the Linux distro name from /etc/os-release, or the OS name."""
    os_release = Path("/etc/os-release")
    if os_release.exists():
        for line in os_release.read_text().splitlines():
            if line.startswith("ID="):
                return line.split("=", 1)[1].strip().strip('"')
    return platform.system().lower()


def get_user_agent() -> str:
    """Build a descriptive User-Agent string."""
    return f"vox-cli/1.0 ({detect_distro()}; {detect_shell()})"
