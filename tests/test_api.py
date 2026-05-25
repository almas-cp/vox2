"""Tests for vox.api — API client with mocked HTTP responses."""

import pytest
import httpx
import respx

from vox.api import ApiError, fetch_command

API_BASE = "https://vox.workers.dev"


@respx.mock
def test_fetch_command_success() -> None:
    route = respx.get(f"{API_BASE}/list%20all%20files").mock(
        return_value=httpx.Response(200, text="ls -la")
    )
    result = fetch_command("list all files")
    assert result == "ls -la"
    assert route.called


@respx.mock
def test_fetch_command_strips_whitespace() -> None:
    respx.get(f"{API_BASE}/hello").mock(
        return_value=httpx.Response(200, text="  echo hello  \n")
    )
    result = fetch_command("hello")
    assert result == "echo hello"


@respx.mock
def test_fetch_command_4xx_raises_immediately() -> None:
    respx.get(f"{API_BASE}/bad").mock(
        return_value=httpx.Response(400, text="bad request")
    )
    with pytest.raises(ApiError, match="API error 400"):
        fetch_command("bad")


@respx.mock
def test_fetch_command_retries_on_5xx() -> None:
    route = respx.get(f"{API_BASE}/retry").mock(
        side_effect=[
            httpx.Response(500, text="error"),
            httpx.Response(500, text="error"),
            httpx.Response(200, text="ok"),
        ]
    )
    result = fetch_command("retry")
    assert result == "ok"
    assert route.call_count == 3


@respx.mock
def test_fetch_command_all_retries_fail() -> None:
    respx.get(f"{API_BASE}/fail").mock(
        side_effect=[
            httpx.Response(500, text="error"),
            httpx.Response(502, text="error"),
            httpx.Response(503, text="error"),
        ]
    )
    with pytest.raises(ApiError, match="Could not reach"):
        fetch_command("fail")
