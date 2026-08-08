"""Corpus storage contracts and reference adapters."""

from .base import CorpusRepository, RankedChunk, RepositoryError, StoredChunk
from .sqlite import SQLiteCorpusRepository

__all__ = [
    "CorpusRepository",
    "RankedChunk",
    "RepositoryError",
    "SQLiteCorpusRepository",
    "StoredChunk",
]
