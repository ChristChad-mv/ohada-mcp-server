"""Small production ASGI middleware with privacy-preserving rate limiting."""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import secrets
import threading
import time
from collections import defaultdict, deque
from collections.abc import MutableMapping
from typing import Any, ClassVar


class PrivacyRateLimitMiddleware:
    """Limit MCP request volume without reading or retaining request bodies.

    Only an ephemeral keyed digest derived from the network address is kept in
    process memory for the duration of the configured window. It is never
    logged or written to disk. Limits apply per Cloud Run instance, providing
    an initial abuse control until an edge limiter is introduced.
    """

    def __init__(
        self,
        app,
        *,
        enabled: bool,
        requests: int,
        window_seconds: int,
        protected_path: str,
        max_clients: int = 10_000,
        trust_proxy_headers: bool = False,
        trusted_proxy_hops: int = 1,
    ) -> None:
        self.app = app
        self.enabled = enabled
        self.requests = requests
        self.window_seconds = window_seconds
        self.protected_path = protected_path.rstrip("/")
        self.max_clients = max_clients
        self.trust_proxy_headers = trust_proxy_headers
        self.trusted_proxy_hops = trusted_proxy_hops
        self._digest_key = secrets.token_bytes(32)
        self._requests: MutableMapping[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @staticmethod
    def _headers(scope: dict[str, Any]) -> dict[str, str]:
        return {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in scope.get("headers", [])}

    def _client_digest(self, scope: dict[str, Any]) -> str:
        headers = self._headers(scope)
        forwarded_values = [value.strip() for value in headers.get("x-forwarded-for", "").split(",") if value.strip()]
        client = scope.get("client") or ("unknown", 0)
        address = str(client[0])

        # Only use forwarding metadata when the deployment explicitly trusts
        # its reverse proxy. Google external load balancers append
        # "client-ip, load-balancer-ip" after any caller-supplied prefix, so
        # the client is one position before the configured trusted proxy hops.
        if self.trust_proxy_headers and len(forwarded_values) > self.trusted_proxy_hops:
            candidate = forwarded_values[-(self.trusted_proxy_hops + 1)]
            try:
                address = str(ipaddress.ip_address(candidate))
            except ValueError:
                pass

        # A process-random HMAC prevents an ephemeral in-memory identifier
        # from being reversed through an IPv4 dictionary attack.
        return hmac.new(self._digest_key, address.encode("utf-8"), hashlib.sha256).hexdigest()

    def _allow(self, key: str, now: float) -> tuple[bool, int, int]:
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.requests:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                return False, 0, retry_after

            bucket.append(now)
            remaining = max(0, self.requests - len(bucket))

            # Bound memory even during a distributed address flood. Oldest
            # insertion order is sufficient because all data is ephemeral.
            if len(self._requests) > self.max_clients:
                stale_keys = [
                    candidate
                    for candidate, timestamps in self._requests.items()
                    if not timestamps or timestamps[-1] <= cutoff
                ]
                for candidate in stale_keys:
                    self._requests.pop(candidate, None)
                while len(self._requests) > self.max_clients:
                    self._requests.pop(next(iter(self._requests)), None)

            return True, remaining, 0

    async def __call__(self, scope, receive, send) -> None:
        path = scope.get("path", "").rstrip("/")
        is_mcp_http = scope.get("type") == "http" and path == self.protected_path

        if self.enabled and is_mcp_http:
            allowed, remaining, retry_after = self._allow(self._client_digest(scope), time.monotonic())
            if not allowed:
                payload = json.dumps(
                    {
                        "error": "rate_limit_exceeded",
                        "message": "Trop de requêtes. Réessayez plus tard.",
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
                headers = [
                    (b"content-type", b"application/json; charset=utf-8"),
                    (b"cache-control", b"no-store"),
                    (b"retry-after", str(retry_after).encode()),
                    (b"x-ratelimit-limit", str(self.requests).encode()),
                    (b"x-ratelimit-remaining", b"0"),
                ]
                await send({"type": "http.response.start", "status": 429, "headers": headers})
                await send({"type": "http.response.body", "body": payload})
                return

            async def send_with_headers(message):
                if message.get("type") == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend(
                        [
                            (b"cache-control", b"no-store"),
                            (b"x-content-type-options", b"nosniff"),
                            (b"x-ratelimit-limit", str(self.requests).encode()),
                            (b"x-ratelimit-remaining", str(remaining).encode()),
                        ]
                    )
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, send_with_headers)
            return

        await self.app(scope, receive, send)


class SecurityHeadersMiddleware:
    """Apply privacy and browser hardening headers to every HTTP response."""

    _BASE_HEADERS: ClassVar[dict[bytes, bytes]] = {
        b"cache-control": b"no-store",
        b"content-security-policy": b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        b"permissions-policy": b"camera=(), microphone=(), geolocation=()",
        b"referrer-policy": b"no-referrer",
        b"x-content-type-options": b"nosniff",
        b"x-frame-options": b"DENY",
    }

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_headers = PrivacyRateLimitMiddleware._headers(scope)
        response_headers = dict(self._BASE_HEADERS)
        if request_headers.get("x-forwarded-proto", "").lower() == "https":
            response_headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"

        async def send_with_security_headers(message):
            if message.get("type") == "http.response.start":
                protected_names = set(response_headers)
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() not in protected_names
                ]
                headers.extend(response_headers.items())
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_security_headers)
