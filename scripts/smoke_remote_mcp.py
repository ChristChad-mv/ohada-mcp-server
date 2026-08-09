"""Validate the deployed MCP handshake, schemas, payloads and basic latency."""

from __future__ import annotations

import argparse
import asyncio
import json
import time

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def smoke(url: str) -> None:
    async with (
        streamable_http_client(url) as (read_stream, write_stream, _),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        tool_list = await session.list_tools()
        tools = {tool.name: tool for tool in tool_list.tools}
        expected = {
            "search_ohada_law",
            "get_article",
            "get_articles",
            "get_act",
            "list_legal_texts",
            "get_version",
            "get_provision_at_date",
            "verify_citation",
            "search_syscohada",
            "get_syscohada_passages",
            "get_syscohada_account",
        }
        if set(tools) != expected:
            raise RuntimeError(f"Outils inattendus : {sorted(tools)}")

        calls = [
            (
                "search_ohada_law",
                {
                    "query": "cessation des paiements déclaration délai commerçant",
                    "max_results": 5,
                    "act_filter": "AUPCAP",
                },
            ),
            ("get_article", {"act_code": "AUSCGIE", "article_reference": "440"}),
            ("get_article", {"act_code": "AUS", "article_reference": "207"}),
            ("get_article", {"act_code": "AUPCAP", "article_reference": "228"}),
            (
                "get_articles",
                {
                    "articles": [
                        {"act_code": "AUPCAP", "article_reference": "2"},
                        {"act_code": "AUPCAP", "article_reference": "25"},
                    ]
                },
            ),
            ("verify_citation", {"citation_text": "Article 326 AUSCGIE"}),
            (
                "search_syscohada",
                {
                    "query": "capital social apports associés",
                    "max_results": 2,
                    "account_filter": "101",
                },
            ),
            ("get_syscohada_account", {"account_code": "101"}),
        ]
        print(f"tools: {len(tools)}")
        syscohada_chunk_ids: list[int] = []
        for name, arguments in calls:
            started = time.perf_counter()
            result = await session.call_tool(name, arguments)
            elapsed_ms = (time.perf_counter() - started) * 1_000
            if result.isError:
                raise RuntimeError(f"{name} a échoué : {result.content}")
            payload = json.dumps(result.model_dump(mode="json"), ensure_ascii=False)
            print(f"{name}: {elapsed_ms:.1f} ms, {len(payload)} caractères JSON")

            structured = result.structuredContent
            if not isinstance(structured, dict):
                raise TypeError(f"{name} n'a pas retourné de structuredContent")
            if name == "search_ohada_law":
                snippets = [item["snippet"] for item in structured["results"]]
                if "result_count" not in structured or any(len(item) > 604 for item in snippets):
                    raise RuntimeError("Contrat de recherche compact invalide")
            elif name == "get_article" and arguments["article_reference"] == "440":
                if "Les délibérations portant approbation" not in structured["text"]:
                    raise RuntimeError("Article 440 incomplet")
            elif name == "get_article" and arguments["article_reference"] == "228":
                if "Article 229" in structured["text"]:
                    raise RuntimeError("Article voisin inclus dans l'article 228")
            elif name == "get_article" and arguments["article_reference"] == "207":
                if "délai maximum de quatre-vingt dix jours" not in structured["text"]:
                    raise RuntimeError("Article 207 incomplet à la limite d'un batch")
            elif name == "get_articles" and structured.get("result_count") != 2:
                raise RuntimeError("Batch d'articles incomplet")
            elif name == "verify_citation" and ("matched_article" in structured or "text" in structured):
                raise RuntimeError("Vérification de citation non compacte")
            elif name == "search_syscohada":
                results = structured.get("results", [])
                if not results or any(item.get("account_code") != "101" for item in results):
                    raise RuntimeError("Recherche SYSCOHADA filtrée incorrecte")
                syscohada_chunk_ids = [item["chunk_id"] for item in results]
            elif name == "get_syscohada_account":
                if structured.get("account_code") != "101" or structured.get("passage_count") != 6:
                    raise RuntimeError("Contexte SYSCOHADA du compte 101 incomplet")
                sources = [item.get("official_source", {}) for item in structured.get("passages", [])]
                if not sources or any(item.get("effective_from") != "2018-01-01" for item in sources):
                    raise RuntimeError("Date d'entrée en vigueur SYSCOHADA absente ou incorrecte")

        started = time.perf_counter()
        passage_result = await session.call_tool(
            "get_syscohada_passages",
            {"chunk_ids": syscohada_chunk_ids},
        )
        elapsed_ms = (time.perf_counter() - started) * 1_000
        if passage_result.isError:
            raise RuntimeError(f"get_syscohada_passages a échoué : {passage_result.content}")
        passages = passage_result.structuredContent
        if not isinstance(passages, dict) or passages.get("result_count") != len(
            syscohada_chunk_ids
        ):
            raise RuntimeError("Récupération des passages SYSCOHADA incomplète")
        print(
            f"get_syscohada_passages: {elapsed_ms:.1f} ms, "
            f"{len(json.dumps(passages, ensure_ascii=False))} caractères JSON"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    asyncio.run(smoke(args.url))


if __name__ == "__main__":
    main()
