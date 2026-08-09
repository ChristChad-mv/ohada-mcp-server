"""Exercise public HTTP security controls without sending a legal question."""

from __future__ import annotations

import argparse

import httpx

REQUIRED_HEADERS = {
    "cache-control": "no-store",
    "content-security-policy": "default-src 'none'",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
    "referrer-policy": "no-referrer",
    "strict-transport-security": "max-age=31536000",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
}


def assert_security_headers(response: httpx.Response) -> None:
    for name, expected in REQUIRED_HEADERS.items():
        actual = response.headers.get(name, "")
        if expected not in actual:
            raise RuntimeError(f"En-tête {name} absent ou invalide : {actual!r}")


def smoke(base_url: str) -> None:
    base_url = base_url.rstrip("/")
    mcp_url = f"{base_url}/mcp"
    initialize = {
        "jsonrpc": "2.0",
        "id": "security-smoke",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "security-smoke", "version": "1"},
        },
    }

    with httpx.Client(timeout=30, follow_redirects=False) as client:
        health = client.get(f"{base_url}/health")
        health.raise_for_status()
        assert_security_headers(health)
        payload = health.json()
        if not payload.get("corpus_ready") or not payload.get("syscohada_ready"):
            raise RuntimeError(f"Corpus indisponible : {payload}")

        bad_host = client.post(
            mcp_url,
            json=initialize,
            headers={
                "accept": "application/json, text/event-stream",
                "host": "attacker.invalid",
            },
        )
        if bad_host.status_code not in {400, 403, 404, 421}:
            raise RuntimeError(f"Host hostile accepté : HTTP {bad_host.status_code}")

        bad_origin = client.post(
            mcp_url,
            json=initialize,
            headers={
                "accept": "application/json, text/event-stream",
                "origin": "https://attacker.invalid",
            },
        )
        if bad_origin.status_code != 403:
            raise RuntimeError(f"Origin hostile accepté : HTTP {bad_origin.status_code}")
        assert_security_headers(bad_origin)

        bad_content_type = client.post(
            mcp_url,
            content=b"not-json",
            headers={
                "accept": "application/json, text/event-stream",
                "content-type": "text/plain",
            },
        )
        if bad_content_type.status_code not in {400, 415}:
            raise RuntimeError(
                f"Content-Type hostile accepté : HTTP {bad_content_type.status_code}"
            )
        assert_security_headers(bad_content_type)

        oversized = client.post(
            mcp_url,
            content=b"x" * 65_537,
            headers={
                "accept": "application/json, text/event-stream",
                "content-type": "application/json",
            },
        )
        if oversized.status_code != 413:
            raise RuntimeError(f"Corps surdimensionné accepté : HTTP {oversized.status_code}")
        assert_security_headers(oversized)

    print("security headers: OK")
    print("host/origin and content-type controls: OK")
    print("request body limit: OK")
    print("both read-only corpora: ready")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    args = parser.parse_args()
    smoke(args.base_url)


if __name__ == "__main__":
    main()
