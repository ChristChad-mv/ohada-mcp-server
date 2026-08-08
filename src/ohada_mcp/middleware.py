"""Small production ASGI middleware with privacy-preserving rate limiting."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from collections.abc import MutableMapping
from typing import Any


class PrivacyRateLimitMiddleware:
    """Limit MCP request volume without reading or retaining request bodies.

    Only an ephemeral SHA-256 digest derived from the network address is kept
    in process memory for the duration of the configured window. It is never
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
    ) -> None:
        self.app = app
        self.enabled = enabled
        self.requests = requests
        self.window_seconds = window_seconds
        self.protected_path = protected_path.rstrip("/")
        self.max_clients = max_clients
        self._requests: MutableMapping[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @staticmethod
    def _headers(scope: dict[str, Any]) -> dict[str, str]:
        return {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in scope.get("headers", [])}

    def _client_digest(self, scope: dict[str, Any]) -> str:
        headers = self._headers(scope)
        # Google Front Ends append the address they observed to any caller-
        # supplied X-Forwarded-For value. Never trust the left-most value: a
        # caller can forge that prefix and otherwise rotate the rate-limit key.
        forwarded_values = [value.strip() for value in headers.get("x-forwarded-for", "").split(",") if value.strip()]
        forwarded = forwarded_values[-1] if forwarded_values else ""
        client = scope.get("client") or ("unknown", 0)
        address = forwarded or str(client[0])
        return hashlib.sha256(address.encode("utf-8")).hexdigest()

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
