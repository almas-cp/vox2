"""Command execution with real-time output streaming."""

from __future__ import annotations

import asyncio
import subprocess
from typing import AsyncGenerator

from vox.utils import detect_shell


async def execute_command(
    cmd: str,
    shell: str | None = None,
    cancel_event: asyncio.Event | None = None,
) -> AsyncGenerator[str, None]:
    """Execute a shell command and yield output lines as they arrive.

    Args:
        cmd: The shell command to run.
        shell: Shell to use (defaults to detected shell).
        cancel_event: Set this event to kill the running process.

    Yields:
        Lines of combined stdout/stderr output.
    """
    shell_bin = shell or detect_shell()
    shell_flag = "-c"
    if shell_bin == "fish":
        shell_flag = "-c"  # fish also uses -c

    proc = await asyncio.create_subprocess_exec(
        shell_bin, shell_flag, cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    try:
        while True:
            if cancel_event and cancel_event.is_set():
                proc.kill()
                yield "\n[cancelled]"
                return

            assert proc.stdout is not None
            try:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            if line:
                yield line.decode("utf-8", errors="replace").rstrip("\n")
            else:
                break
    except Exception as exc:
        yield f"\n[error: {exc}]"
    finally:
        try:
            await proc.wait()
        except Exception:
            pass

    code = proc.returncode
    if code and code != 0:
        yield f"\n[exit code: {code}]"


def execute_command_sync(cmd: str, shell: str | None = None) -> subprocess.CompletedProcess[str]:
    """Synchronous execution for --no-tui mode."""
    shell_bin = shell or detect_shell()
    return subprocess.run(
        [shell_bin, "-c", cmd],
        capture_output=False,
        text=True,
    )
