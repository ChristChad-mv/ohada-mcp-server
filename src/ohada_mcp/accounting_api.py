"""SYSCOHADA accounting tools exposed alongside the normative legal API."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ohada_mcp.config import settings
from ohada_mcp.models import (
    OfficialSource,
    SyscohadaAccountContext,
    SyscohadaPassage,
    SyscohadaPassageBatch,
    SyscohadaSearchResultItem,
    SyscohadaSearchResults,
)
from ohada_mcp.repositories.syscohada_sqlite import (
    SQLiteSyscohadaRepository,
    StoredSyscohadaChunk,
)

DEFAULT_SYSCOHADA_DB_PATH = settings.OHADA_SYSCOHADA_DB_PATH.expanduser()
if not DEFAULT_SYSCOHADA_DB_PATH.is_absolute():
    DEFAULT_SYSCOHADA_DB_PATH = Path.cwd() / DEFAULT_SYSCOHADA_DB_PATH


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", plain.lower()).strip()


def _snippet(text: str, query: str, limit: int = 600) -> str:
    cleaned = re.sub(r"^\[[^\]\n]*\]\s*", "", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    terms = [term for term in _normalize(query).split() if len(term) >= 4]
    normalized = _normalize(cleaned)
    positions = [normalized.find(term) for term in terms if normalized.find(term) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - limit // 3)
    end = min(len(cleaned), start + limit)
    prefix = "…" if start else ""
    suffix = "…" if end < len(cleaned) else ""
    return f"{prefix}{cleaned[start:end].strip()}{suffix}"


def _source() -> OfficialSource:
    return OfficialSource(
        publisher="Secrétariat Permanent de l'OHADA",
        publication="Journal Officiel de l'OHADA n° spécial du 15/02/2017",
        adopted_at="2017-01-26",
        published_at="2017-02-15",
        effective_from="2018-01-01",
        url="https://biblio.ohada.org/doc_num.php?explnum_id=2063",
    )


def _citation(metadata: dict) -> str:
    account = metadata.get("account_code")
    start = metadata.get("page_start")
    end = metadata.get("page_end")
    locator = f"compte {account}" if account else "publication officielle"
    pages = f"p. {start}" if not end or start == end else f"pp. {start}-{end}"
    return f"SYSCOHADA — {locator}, {pages}"


class SyscohadaClient:
    def __init__(
        self,
        db_path: str | Path | None = None,
        repository: SQLiteSyscohadaRepository | None = None,
    ):
        self.repository = repository or SQLiteSyscohadaRepository(
            db_path or DEFAULT_SYSCOHADA_DB_PATH
        )

    @property
    def db_path(self) -> Path:
        return self.repository.db_path

    @db_path.setter
    def db_path(self, value: str | Path) -> None:
        self.repository.db_path = Path(value)

    @staticmethod
    def _passage(row: StoredSyscohadaChunk) -> SyscohadaPassage:
        metadata = row.metadata
        return SyscohadaPassage(
            chunk_id=row.id,
            hierarchy_path=row.hierarchy_path,
            text=row.text_content,
            page_start=int(metadata["page_start"]),
            page_end=int(metadata["page_end"]),
            class_code=metadata.get("class_code"),
            class_label=metadata.get("class_label"),
            account_code=metadata.get("account_code"),
            account_label=metadata.get("account_label"),
            account_subsection=metadata.get("account_subsection"),
            application_id=metadata.get("application_id"),
            application_label=metadata.get("application_label"),
            is_table=bool(metadata.get("is_table")),
            citation=_citation(metadata),
            official_source=_source(),
        )

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        account_filter: str | None = None,
        class_filter: str | None = None,
    ) -> SyscohadaSearchResults:
        rows = self.repository.search(
            query,
            candidate_limit=max(max_results * 20, 80),
            account_filter=account_filter,
            class_filter=class_filter,
        )
        terms = {term for term in _normalize(query).split() if len(term) >= 3}

        def quality(item: tuple[int, StoredSyscohadaChunk]) -> tuple[int, int, int]:
            position, row = item
            searchable = _normalize(f"{row.hierarchy_path} {row.text_content}")
            coverage = sum(term in searchable for term in terms)
            repeated = sum(min(searchable.count(term), 2) for term in terms)
            return coverage, repeated, -position

        ranked = [row for _, row in sorted(enumerate(rows), key=quality, reverse=True)]
        results: list[SyscohadaSearchResultItem] = []
        seen: set[tuple[str, int, int]] = set()
        for row in ranked:
            metadata = row.metadata
            key = (
                row.hierarchy_path,
                int(metadata["page_start"]),
                int(metadata["page_end"]),
            )
            if key in seen:
                continue
            seen.add(key)
            results.append(
                SyscohadaSearchResultItem(
                    rank=len(results) + 1,
                    chunk_id=row.id,
                    hierarchy_path=row.hierarchy_path,
                    snippet=_snippet(row.text_content, query),
                    page_start=int(metadata["page_start"]),
                    page_end=int(metadata["page_end"]),
                    class_code=metadata.get("class_code"),
                    class_label=metadata.get("class_label"),
                    account_code=metadata.get("account_code"),
                    account_label=metadata.get("account_label"),
                    account_subsection=metadata.get("account_subsection"),
                    is_table=bool(metadata.get("is_table")),
                )
            )
            if len(results) >= max_results:
                break
        return SyscohadaSearchResults(
            query=query,
            result_count=len(results),
            account_filter=account_filter,
            class_filter=class_filter,
            results=results,
        )

    async def passages(self, chunk_ids: list[int]) -> SyscohadaPassageBatch:
        rows = self.repository.passages(chunk_ids)
        found = {row.id for row in rows}
        return SyscohadaPassageBatch(
            requested_count=len(chunk_ids),
            result_count=len(rows),
            passages=[self._passage(row) for row in rows],
            missing_chunk_ids=[chunk_id for chunk_id in chunk_ids if chunk_id not in found],
        )

    async def account(self, account_code: str) -> SyscohadaAccountContext:
        rows = self.repository.account(account_code)
        if not rows:
            raise ValueError(f"Compte {account_code} introuvable dans le corpus SYSCOHADA.")
        passages = [self._passage(row) for row in rows]
        account_label = next((item.account_label for item in passages if item.account_label), None)
        return SyscohadaAccountContext(
            account_code=account_code,
            account_label=account_label,
            passage_count=len(passages),
            passages=passages,
        )


syscohada_client = SyscohadaClient()


async def search_syscohada(
    query: str,
    max_results: int = 5,
    account_filter: str | None = None,
    class_filter: str | None = None,
) -> SyscohadaSearchResults:
    query = query.strip()
    if not query:
        raise ValueError("La requête SYSCOHADA ne peut pas être vide.")
    if len(query) > settings.MAX_QUERY_LENGTH:
        raise ValueError(f"La requête dépasse la limite de {settings.MAX_QUERY_LENGTH} caractères.")
    terms = re.findall(r"\w+", query, flags=re.UNICODE)
    if not terms:
        raise ValueError("La requête doit contenir au moins un terme alphanumérique.")
    if len(terms) > settings.MAX_QUERY_TERMS:
        raise ValueError(f"La requête dépasse la limite de {settings.MAX_QUERY_TERMS} termes.")
    if not 1 <= max_results <= settings.MAX_SEARCH_RESULTS:
        raise ValueError(f"max_results doit être compris entre 1 et {settings.MAX_SEARCH_RESULTS}.")
    if account_filter is not None and not re.fullmatch(r"\d{2,4}", account_filter.strip()):
        raise ValueError("account_filter doit contenir un code de compte de 2 à 4 chiffres.")
    if class_filter is not None and not re.fullmatch(r"\d", class_filter.strip()):
        raise ValueError("class_filter doit contenir un chiffre de classe.")
    return await syscohada_client.search(
        query,
        max_results=max_results,
        account_filter=account_filter.strip() if account_filter else None,
        class_filter=class_filter.strip() if class_filter else None,
    )


async def get_syscohada_passages(chunk_ids: list[int]) -> SyscohadaPassageBatch:
    if not 1 <= len(chunk_ids) <= 5:
        raise ValueError("chunk_ids doit contenir entre 1 et 5 identifiants.")
    if len(set(chunk_ids)) != len(chunk_ids) or any(chunk_id < 1 for chunk_id in chunk_ids):
        raise ValueError("chunk_ids doit contenir des identifiants positifs et distincts.")
    return await syscohada_client.passages(chunk_ids)


async def get_syscohada_account(account_code: str) -> SyscohadaAccountContext:
    account_code = str(account_code).strip()
    if not re.fullmatch(r"\d{2,4}", account_code):
        raise ValueError("account_code doit contenir un code de compte de 2 à 4 chiffres.")
    return await syscohada_client.account(account_code)
