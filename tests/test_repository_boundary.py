"""The legal domain service must operate through a storage-neutral contract."""

from pathlib import Path

import pytest
from ohada_mcp.catalog import OHADA_CATALOGUE
from ohada_mcp.client import CorpusBackendClient
from ohada_mcp.repositories import RankedChunk, StoredChunk


class InMemoryCorpusRepository:
    def __init__(self):
        self.db_path = Path("memory-corpus")
        self.file_name = OHADA_CATALOGUE["AUSCGIE"]["file"]
        self.chunks = [
            StoredChunk(1, "Révocation > Article 326", "[Article 326]\nPremier alinéa."),
            StoredChunk(2, "Révocation > Article 326", "[Article 326]\nDernier alinéa."),
        ]

    def chunks_for_document(self, document_name):
        return self.chunks if document_name == self.file_name else []

    def article_path_candidates(self, document_name, article_reference):
        if document_name != self.file_name or article_reference != "326":
            return []
        return self.chunks

    def article_text_candidates(self, _document_name, _article_reference):
        return []

    def search_chunks(self, _query, *, candidate_limit, document_name=None):
        if document_name not in {None, self.file_name}:
            return []
        return [
            RankedChunk(
                id=1,
                hierarchy_path=self.chunks[0].hierarchy_path,
                text_content=self.chunks[0].text_content,
                document_name=self.file_name,
                storage_rank=0.0,
            )
        ][:candidate_limit]

    def structure_paths(self, document_name, limit=50):
        if document_name != self.file_name:
            return []
        return [self.chunks[0].hierarchy_path][:limit]


@pytest.mark.asyncio
async def test_domain_service_accepts_a_non_sql_repository():
    service = CorpusBackendClient(repository=InMemoryCorpusRepository())

    article = await service.get_article("AUSCGIE", "326")
    results = await service.search("révocation", act_filter="AUSCGIE")

    assert article.text == "Premier alinéa.\nDernier alinéa."
    assert results.results[0].article_reference == "326"
