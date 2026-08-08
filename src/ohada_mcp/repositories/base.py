"""Storage-neutral contracts consumed by the OHADA legal domain service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class RepositoryError(RuntimeError):
    """The corpus backend failed without exposing storage internals."""


@dataclass(frozen=True)
class StoredChunk:
    id: int
    hierarchy_path: str
    text_content: str


@dataclass(frozen=True)
class RankedChunk(StoredChunk):
    document_name: str
    storage_rank: float = 0.0


class CorpusRepository(Protocol):
    """Minimal persistence boundary required by the MCP domain layer."""

    db_path: Path

    def chunks_for_document(self, document_name: str) -> list[StoredChunk]: ...

    def article_path_candidates(self, document_name: str, article_reference: str) -> list[StoredChunk]: ...

    def article_text_candidates(self, document_name: str, article_reference: str) -> list[StoredChunk]: ...

    def search_chunks(
        self,
        query: str,
        *,
        candidate_limit: int,
        document_name: str | None = None,
    ) -> list[RankedChunk]: ...

    def structure_paths(self, document_name: str, limit: int = 50) -> list[str]: ...
