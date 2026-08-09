"""Privacy-preserving rate limiter tests."""

import json

import pytest
from ohada_mcp.middleware import PrivacyRateLimitMiddleware, SecurityHeadersMiddleware


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
    forwarded_proto=None,
):
    messages = []
    headers = [(b"x-forwarded-for", (forwarded_for or address).encode())]
    if forwarded_proto:
        headers.append((b"x-forwarded-proto", forwarded_proto.encode()))
    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": headers,
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
        trust_proxy_headers=True,
        trusted_proxy_hops=1,
    )

    assert (
        await _request(
            limiter,
            forwarded_for="198.51.100.1, 203.0.113.10, 192.0.2.1",
        )
    )[0]["status"] == 200
    blocked = await _request(
        limiter,
        forwarded_for="198.51.100.99, 203.0.113.10, 192.0.2.1",
    )

    assert blocked[0]["status"] == 429


@pytest.mark.asyncio
async def test_forwarded_headers_are_ignored_without_explicit_proxy_trust():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=1,
        window_seconds=60,
        protected_path="/mcp",
    )

    assert (
        await _request(limiter, address="127.0.0.1", forwarded_for="198.51.100.1")
    )[0]["status"] == 200
    blocked = await _request(
        limiter,
        address="127.0.0.1",
        forwarded_for="198.51.100.99",
    )

    assert blocked[0]["status"] == 429


@pytest.mark.asyncio
async def test_distinct_clients_behind_the_same_trusted_proxy_have_distinct_quotas():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=1,
        window_seconds=60,
        protected_path="/mcp",
        trust_proxy_headers=True,
        trusted_proxy_hops=1,
    )

    first = await _request(
        limiter,
        address="127.0.0.1",
        forwarded_for="198.51.100.1, 203.0.113.10, 192.0.2.1",
    )
    second = await _request(
        limiter,
        address="127.0.0.1",
        forwarded_for="198.51.100.1, 203.0.113.11, 192.0.2.1",
    )

    assert first[0]["status"] == 200
    assert second[0]["status"] == 200


@pytest.mark.asyncio
async def test_security_headers_cover_success_and_rate_limit_responses():
    limiter = PrivacyRateLimitMiddleware(
        _ok_app,
        enabled=True,
        requests=1,
        window_seconds=60,
        protected_path="/mcp",
    )
    app = SecurityHeadersMiddleware(limiter)

    success = await _request(app, forwarded_proto="https")
    blocked = await _request(app, forwarded_proto="https")

    for response in (success, blocked):
        headers = dict(response[0]["headers"])
        assert headers[b"cache-control"] == b"no-store"
        assert headers[b"content-security-policy"].startswith(b"default-src 'none'")
        assert headers[b"permissions-policy"] == b"camera=(), microphone=(), geolocation=()"
        assert headers[b"referrer-policy"] == b"no-referrer"
        assert headers[b"x-content-type-options"] == b"nosniff"
        assert headers[b"x-frame-options"] == b"DENY"
        assert headers[b"strict-transport-security"] == b"max-age=31536000; includeSubDomains"


@pytest.mark.asyncio
async def test_hsts_is_not_sent_for_plain_local_http():
    app = SecurityHeadersMiddleware(_ok_app)

    response = await _request(app)

    assert b"strict-transport-security" not in dict(response[0]["headers"])
