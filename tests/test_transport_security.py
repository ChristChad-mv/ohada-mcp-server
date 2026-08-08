"""Transport security regression tests."""

import pytest
from mcp.server.transport_security import TransportSecurityMiddleware
from ohada_mcp.server import transport_security
from starlette.requests import Request


def _request(*, host: str, origin: str | None = None, content_type: str = "application/json"):
    headers = [(b"host", host.encode()), (b"content-type", content_type.encode())]
    if origin:
        headers.append((b"origin", origin.encode()))
    return Request({"type": "http", "method": "POST", "path": "/mcp", "headers": headers})


@pytest.mark.asyncio
async def test_transport_rejects_unlisted_host():
    middleware = TransportSecurityMiddleware(transport_security)
    response = await middleware.validate_request(_request(host="attacker.example"), is_post=True)
    assert response is not None
    assert response.status_code == 421


@pytest.mark.asyncio
async def test_transport_accepts_configured_local_host():
    middleware = TransportSecurityMiddleware(transport_security)
    response = await middleware.validate_request(
        _request(host="localhost:8080", origin="http://localhost:3000"),
        is_post=True,
    )
    assert response is None


@pytest.mark.asyncio
async def test_transport_rejects_non_json_post():
    middleware = TransportSecurityMiddleware(transport_security)
    response = await middleware.validate_request(
        _request(host="localhost:8080", content_type="text/plain"), is_post=True
    )
    assert response is not None
    assert response.status_code == 400
