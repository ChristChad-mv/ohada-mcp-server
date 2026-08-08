"""Audit canonical article reconstruction against a compatible corpus database."""

from __future__ import annotations

import argparse
import asyncio
import re
import sqlite3
from pathlib import Path

from ohada_mcp.catalog import OHADA_CATALOGUE
from ohada_mcp.client import (
    CorpusBackendClient,
    _article_reference_from_path,
    _clean_article_chunk,
    _embedded_article_segments,
    _following_article_continuations,
    _select_article_rows,
)
from ohada_mcp.repositories import StoredChunk


async def audit(db_path: Path) -> int:
    client = CorpusBackendClient(str(db_path))
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    failures: list[str] = []
    checked_articles = 0
    multi_chunk_articles = 0
    batch_boundary_articles = 0

    for act_code, info in OHADA_CATALOGUE.items():
        raw_rows = connection.execute(
            """
            SELECT c.id, c.hierarchy_path, c.text_content
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.name = ?
            ORDER BY c.id
            """,
            (info["file"],),
        ).fetchall()
        rows = [
            StoredChunk(
                id=row["id"],
                hierarchy_path=row["hierarchy_path"],
                text_content=row["text_content"],
            )
            for row in raw_rows
        ]
        references = {reference for row in rows if (reference := _article_reference_from_path(row.hierarchy_path))}
        for row in rows:
            references.update(_embedded_article_segments(row.text_content))

        for reference in sorted(references):
            selected = _select_article_rows(rows, reference)
            if selected:
                exact_parts = [cleaned for row in selected if (cleaned := _clean_article_chunk(row.text_content))]
                continuations = _following_article_continuations(rows, selected, reference)
                expected = "\n".join([*exact_parts, *continuations])
            else:
                continuations = []
                embedded = [
                    segment for row in rows if (segment := _embedded_article_segments(row.text_content).get(reference))
                ]
                if not embedded:
                    failures.append(f"{act_code} Article {reference}: aucun texte sélectionné")
                    continue
                expected = max(embedded, key=len)
            article = await client.get_article(act_code, reference)
            checked_articles += 1
            if selected and len(selected) > 1:
                multi_chunk_articles += 1
            if continuations:
                batch_boundary_articles += 1

            if article.text != expected:
                failures.append(f"{act_code} Article {reference}: reconstruction différente ({len(selected)} chunks)")
            if article.text.startswith("["):
                failures.append(f"{act_code} Article {reference}: préfixe d'index non retiré")
            if re.search(
                r"\b(?:un|une|le|la|les|de|des|du|à|au|aux|et|ou|pour|dans|par|sur)\s*$", article.text, re.IGNORECASE
            ):
                failures.append(f"{act_code} Article {reference}: fin de phrase probablement tronquée")

    connection.close()
    print(f"Articles contrôlés : {checked_articles}")
    print(f"Articles multi-chunks reconstruits : {multi_chunk_articles}")
    print(f"Articles prolongés aux limites de batch : {batch_boundary_articles}")
    print(f"Erreurs : {len(failures)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", type=Path, help="Chemin de la base SQLite à auditer")
    args = parser.parse_args()
    if not args.db_path.is_file():
        parser.error(f"Base introuvable : {args.db_path}")
    raise SystemExit(asyncio.run(audit(args.db_path)))


if __name__ == "__main__":
    main()
