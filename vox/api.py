"""API client for vox.workers.dev with retry logic."""

from __future__ import annotations

import urllib.parse
from typing import TYPE_CHECKING

import httpx

from vox.utils import detect_distro, detect_shell, get_user_agent

if TYPE_CHECKING:
    pass

API_BASE = "https://vox.almaas.workers.dev"
TIMEOUT = 15.0
MAX_RETRIES = 3


class ApiError(Exception):
    """Raised when the API call fails after all retries."""


def fetch_command(query: str) -> str:
    """Send a natural language query and return the generated shell command.

    Retries up to MAX_RETRIES times with exponential backoff.
    """
    encoded = urllib.parse.quote(query, safe="")
    url = f"{API_BASE}/{encoded}"
    headers = {
        "User-Agent": get_user_agent(),
        "X-Shell": detect_shell(),
        "X-Distro": detect_distro(),
    }

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=TIMEOUT) as client:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.text.strip()
        except httpx.ConnectError as exc:
            last_exc = exc
            # No point retrying connection failures quickly
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(2 ** attempt)
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            if exc.response.status_code < 500:
                raise ApiError(f"API error {exc.response.status_code}: {exc.response.text}") from exc
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(2 ** attempt)
        except httpx.TimeoutException as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(2 ** attempt)

    raise ApiError(
        "Could not reach vox API after retries. Check your internet connection."
    ) from last_exc


async def fetch_command_async(query: str) -> str:
    """Async version for use inside Textual workers."""
    encoded = urllib.parse.quote(query, safe="")
    url = f"{API_BASE}/{encoded}"
    headers = {
        "User-Agent": get_user_agent(),
        "X-Shell": detect_shell(),
        "X-Distro": detect_distro(),
    }

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.text.strip()
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            if exc.response.status_code < 500:
                raise ApiError(f"API error {exc.response.status_code}: {exc.response.text}") from exc
            if attempt < MAX_RETRIES - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)

    raise ApiError(
        "Could not reach vox API after retries. Check your internet connection."
    ) from last_exc
