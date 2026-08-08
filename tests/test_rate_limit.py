"""Privacy-preserving rate limiter tests."""

import json

import pytest
from ohada_mcp.middleware import PrivacyRateLimitMiddleware


async def _ok_app(scope, receive, send):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": b"{}"})


async def _request(
    app,
    *,
    path="/mcp",
    address="203.0.113.10",
    forwarded_for=None,
):
    messages = []
    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": [(b"x-forwarded-for", (forwarded_for or address).encode())],
        "client": (address, 12345),
    }

    async def receive():
        return {"type": "http.request", "body": b'{"query":"not inspected"}'}

    async def send(message):
        messages.append(message)

    await app(scope, receive, send)
    return messages


@pytest.mark.asyncio
async def test_rate_limit_returns_429_without_reading_body():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=2,
        window_seconds=60,
        protected_path="/mcp",
    )

    assert (await _request(limiter))[0]["status"] == 200
    assert (await _request(limiter))[0]["status"] == 200
    blocked = await _request(limiter)

    assert blocked[0]["status"] == 429
    payload = json.loads(blocked[1]["body"])
    assert payload["error"] == "rate_limit_exceeded"
    assert all("not inspected" not in str(value) for value in limiter._requests.values())


@pytest.mark.asyncio
async def test_health_path_is_not_rate_limited():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=1,
        window_seconds=60,
        protected_path="/mcp",
    )

    assert (await _request(limiter, path="/health"))[0]["status"] == 200
    assert (await _request(limiter, path="/health"))[0]["status"] == 200


@pytest.mark.asyncio
async def test_caller_supplied_forwarded_prefix_cannot_rotate_limit_key():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=1,
        window_seconds=60,
        protected_path="/mcp",
    )

    assert (
        await _request(
            limiter,
            forwarded_for="198.51.100.1, 203.0.113.10",
        )
    )[0]["status"] == 200
    blocked = await _request(
        limiter,
        forwarded_for="198.51.100.99, 203.0.113.10",
    )

    assert blocked[0]["status"] == 429
