"""Read-only SQLite repository for the prepared SYSCOHADA corpus."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import RepositoryError


@dataclass(frozen=True)
class StoredSyscohadaChunk:
    id: int
    hierarchy_path: str
    text_content: str
    metadata: dict[str, Any]
    storage_rank: float = 0.0


class SQLiteSyscohadaRepository:
    """Deterministic FTS and exact lookup over a SYSCOHADA SQLite index."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.is_file():
            raise FileNotFoundError(f"Base SYSCOHADA introuvable: {self.db_path}")
        # The production corpus is an immutable image layer. Opening it through
        # SQLite's read-only immutable URI prevents attempts to create WAL/SHM
        # sidecars in the non-writable application directory.
        database_uri = f"{self.db_path.resolve().as_uri()}?mode=ro&immutable=1"
        connection = sqlite3.connect(database_uri, uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _chunk(row: sqlite3.Row) -> StoredSyscohadaChunk:
        try:
            metadata = json.loads(row["metadata_json"] or "{}")
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        return StoredSyscohadaChunk(
            id=int(row["id"]),
            hierarchy_path=str(row["hierarchy_path"]),
            text_content=str(row["text_content"]),
            metadata=metadata if isinstance(metadata, dict) else {},
            storage_rank=float(row["storage_rank"]),
        )

    def search(
        self,
        query: str,
        *,
        candidate_limit: int,
        account_filter: str | None = None,
        class_filter: str | None = None,
    ) -> list[StoredSyscohadaChunk]:
        clean_query = re.sub(r"[^\w\s]", " ", query).strip()
        fts_query = " OR ".join(clean_query.split())
        if not fts_query:
            return []
        sql = """
            SELECT c.id, c.hierarchy_path, c.text_content, c.metadata_json,
                   rank AS storage_rank
              FROM chunks_fts fts
              JOIN chunks c ON fts.rowid = c.id
             WHERE chunks_fts MATCH ?
               AND JSON_EXTRACT(c.metadata_json, '$.document_type') = 'syscohada'
        """
        parameters: list[object] = [fts_query]
        if account_filter:
            sql += " AND JSON_EXTRACT(c.metadata_json, '$.account_code') = ?"
            parameters.append(account_filter)
        if class_filter:
            sql += " AND JSON_EXTRACT(c.metadata_json, '$.class_code') = ?"
            parameters.append(class_filter)
        sql += " ORDER BY rank LIMIT ?"
        parameters.append(candidate_limit)
        try:
            with self._connect() as connection:
                rows = connection.execute(sql, parameters).fetchall()
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de recherche dans le corpus SYSCOHADA.") from exc
        return [self._chunk(row) for row in rows]

    def passages(self, chunk_ids: list[int]) -> list[StoredSyscohadaChunk]:
        if not chunk_ids:
            return []
        placeholders = ",".join("?" for _ in chunk_ids)
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    f"""
                    SELECT id, hierarchy_path, text_content, metadata_json,
                           0.0 AS storage_rank
                      FROM chunks
                     WHERE id IN ({placeholders})
                       AND JSON_EXTRACT(metadata_json, '$.document_type') = 'syscohada'
                    """,
                    chunk_ids,
                ).fetchall()
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de lecture des passages SYSCOHADA.") from exc
        by_id = {int(row["id"]): self._chunk(row) for row in rows}
        return [by_id[chunk_id] for chunk_id in chunk_ids if chunk_id in by_id]

    def account(self, account_code: str) -> list[StoredSyscohadaChunk]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, hierarchy_path, text_content, metadata_json,
                           0.0 AS storage_rank
                      FROM chunks
                     WHERE JSON_EXTRACT(metadata_json, '$.document_type') = 'syscohada'
                       AND JSON_EXTRACT(metadata_json, '$.account_code') = ?
                     ORDER BY id
                    """,
                    (account_code,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise RepositoryError("Échec de lecture du compte SYSCOHADA.") from exc
        return [self._chunk(row) for row in rows]
