"""Measure local tool latency and JSON payload size on a compatible corpus."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from ohada_mcp import legal_api
from ohada_mcp.client import corpus_client


async def benchmark(db_path: Path) -> None:
    corpus_client.db_path = db_path
    cases = [
        (
            "search_ohada_law",
            legal_api.search_ohada_law(
                "cessation des paiements déclaration délai commerçant",
                max_results=5,
                act_filter="AUPCAP",
            ),
        ),
        ("get_article", legal_api.get_article("AUPCAP", "25")),
        ("verify_citation", legal_api.verify_citation("Article 25 AUPCAP")),
        (
            "get_articles",
            legal_api.get_articles(
                [
                    {"act_code": "AUPCAP", "article_reference": "1-1"},
                    {"act_code": "AUPCAP", "article_reference": "2"},
                    {"act_code": "AUPCAP", "article_reference": "25"},
                ]
            ),
        ),
    ]

    for name, operation in cases:
        started = time.perf_counter()
        result = await operation
        elapsed_ms = (time.perf_counter() - started) * 1_000
        payload = json.dumps(result.model_dump(mode="json"), ensure_ascii=False)
        print(f"{name}: {elapsed_ms:.1f} ms, {len(payload)} caractères JSON")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", type=Path)
    args = parser.parse_args()
    if not args.db_path.is_file():
        parser.error(f"Base introuvable : {args.db_path}")
    asyncio.run(benchmark(args.db_path))


if __name__ == "__main__":
    main()
