"""SQLite FTS5 reference adapter for self-hosted OHADA MCP deployments."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from .base import RankedChunk, RepositoryError, StoredChunk


class SQLiteCorpusRepository:
    """Boring, deterministic reference storage; the corpus itself stays private."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.is_file():
            raise FileNotFoundError(f"Database OHADA introuvable: {self.db_path}")
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _stored(rows: list[sqlite3.Row]) -> list[StoredChunk]:
        return [
            StoredChunk(
                id=row["id"],
                hierarchy_path=row["hierarchy_path"],
                text_content=row["text_content"],
            )
            for row in rows
        ]

    def chunks_for_document(self, document_name: str) -> list[StoredChunk]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT c.id, c.hierarchy_path, c.text_content
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE d.name = ?
                    ORDER BY c.id
                    """,
                    (document_name,),
                ).fetchall()
            return self._stored(rows)
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de lecture du corpus SQLite.") from exc

    def article_path_candidates(self, document_name: str, article_reference: str) -> list[StoredChunk]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT c.id, c.hierarchy_path, c.text_content
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE d.name = ? AND c.hierarchy_path LIKE ?
                    ORDER BY c.id
                    """,
                    (document_name, f"%Article {article_reference}%"),
                ).fetchall()
            return self._stored(rows)
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de résolution d'article.") from exc

    def article_text_candidates(self, document_name: str, article_reference: str) -> list[StoredChunk]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT c.id, c.hierarchy_path, c.text_content
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE d.name = ? AND c.text_content LIKE ?
                    ORDER BY c.id
                    """,
                    (document_name, f"%Article {article_reference}%"),
                ).fetchall()
            return self._stored(rows)
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de résolution d'article imbriqué.") from exc

    def search_chunks(
        self,
        query: str,
        *,
        candidate_limit: int,
        document_name: str | None = None,
    ) -> list[RankedChunk]:
        clean_query = re.sub(r"[^\w\s]", " ", query).strip()
        fts_query = " OR ".join(clean_query.split()) if clean_query else query
        try:
            with self._connect() as connection:
                sql = """
                    SELECT c.id, c.hierarchy_path, c.text_content,
                           d.name AS document_name, rank
                    FROM chunks_fts fts
                    JOIN chunks c ON fts.rowid = c.id
                    JOIN documents d ON c.document_id = d.id
                """
                parameters: list[object] = []
                if document_name:
                    sql += " WHERE d.name = ? AND chunks_fts MATCH ?"
                    parameters.extend([document_name, fts_query])
                else:
                    sql += " WHERE chunks_fts MATCH ?"
                    parameters.append(fts_query)
                sql += " ORDER BY rank LIMIT ?"
                parameters.append(candidate_limit)
                rows = connection.execute(sql, parameters).fetchall()

                if not rows:
                    sql = """
                        SELECT c.id, c.hierarchy_path, c.text_content,
                               d.name AS document_name, 0.0 AS rank
                        FROM chunks c
                        JOIN documents d ON c.document_id = d.id
                        WHERE c.text_content LIKE ?
                    """
                    parameters = [f"%{clean_query}%"]
                    if document_name:
                        sql += " AND d.name = ?"
                        parameters.append(document_name)
                    sql += " LIMIT ?"
                    parameters.append(candidate_limit)
                    rows = connection.execute(sql, parameters).fetchall()
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de recherche dans le corpus SQLite.") from exc

        return [
            RankedChunk(
                id=row["id"],
                hierarchy_path=row["hierarchy_path"],
                text_content=row["text_content"],
                document_name=row["document_name"],
                storage_rank=float(row["rank"]),
            )
            for row in rows
        ]

    def structure_paths(self, document_name: str, limit: int = 50) -> list[str]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT DISTINCT c.hierarchy_path
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE d.name = ?
                    ORDER BY c.id
                    LIMIT ?
                    """,
                    (document_name, limit),
                ).fetchall()
            return [row["hierarchy_path"] for row in rows]
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de lecture de la structure du corpus.") from exc
