"""
Normative Legal API Services.

Implements domain-specific legal calculations, temporal resolution (tempus regit actum),
and citation verification wrappers.
"""

import re
from datetime import date
from typing import Any

from ohada_mcp.catalog import OHADA_CATALOGUE
from ohada_mcp.client import corpus_client
from ohada_mcp.config import settings
from ohada_mcp.models import (
    ArticleBatch,
    ArticleLocator,
    ArticleLookupError,
    CitationVerificationResult,
    LegalAct,
    LegalArticle,
    LegalTextSummary,
    SearchResults,
    TemporalApplicabilityResult,
)


async def search_ohada_law(query: str, max_results: int = 5, act_filter: str | None = None) -> SearchResults:
    """Run full-text legal search across the indexed OHADA texts."""
    query = query.strip()
    if not query:
        raise ValueError("La requête de recherche ne peut pas être vide.")
    if len(query) > settings.MAX_QUERY_LENGTH:
        raise ValueError(f"La requête dépasse la limite de {settings.MAX_QUERY_LENGTH} caractères.")
    terms = re.findall(r"\w+", query, flags=re.UNICODE)
    if not terms:
        raise ValueError("La requête doit contenir au moins un terme alphanumérique.")
    if len(terms) > settings.MAX_QUERY_TERMS:
        raise ValueError(f"La requête dépasse la limite de {settings.MAX_QUERY_TERMS} termes.")
    if not 1 <= max_results <= settings.MAX_SEARCH_RESULTS:
        raise ValueError(f"max_results doit être compris entre 1 et {settings.MAX_SEARCH_RESULTS}.")
    return await corpus_client.search(query=query, limit=max_results, act_filter=act_filter)


async def get_article(act_code: str, article_reference: str) -> LegalArticle:
    """Retrieve canonical LegalArticle by act code and reference string (e.g. '16', '13 bis', '655-1')."""
    article_reference = str(article_reference).strip()
    if not re.fullmatch(
        r"\d+(?:[-.]\d+)*(?:\s+(?:bis|ter|quater))?",
        article_reference,
        flags=re.IGNORECASE,
    ):
        raise ValueError("Référence d'article invalide.")
    return await corpus_client.get_article(act_code=act_code, article_reference=article_reference)


async def get_articles(articles: list[ArticleLocator | dict[str, str]]) -> ArticleBatch:
    """Retrieve two to five exact articles while isolating per-item lookup errors."""
    if not 2 <= len(articles) <= 5:
        raise ValueError("articles doit contenir entre 2 et 5 références.")

    locators = [item if isinstance(item, ArticleLocator) else ArticleLocator.model_validate(item) for item in articles]
    unique_locators = list(
        dict.fromkeys((item.act_code.upper().strip(), item.article_reference.strip().lower()) for item in locators)
    )
    if len(unique_locators) != len(locators):
        raise ValueError("articles ne doit pas contenir de référence dupliquée.")

    results: list[LegalArticle] = []
    errors: list[ArticleLookupError] = []
    for act_code, article_reference in unique_locators:
        try:
            results.append(await get_article(act_code, article_reference))
        except (FileNotFoundError, ValueError):
            errors.append(
                ArticleLookupError(
                    act_code=act_code,
                    article_reference=article_reference,
                    error=f"Article {article_reference} introuvable dans l'Acte {act_code}.",
                )
            )

    return ArticleBatch(
        requested_count=len(locators),
        result_count=len(results),
        articles=results,
        errors=errors,
    )


async def get_act(act_code: str) -> LegalAct:
    """Retrieve complete metadata and structure for a Uniform Act."""
    return await corpus_client.get_act(act_code=act_code)


async def list_legal_texts() -> list[LegalTextSummary]:
    """Retrieve a compact catalogue; use get_act for complete metadata."""
    return [
        LegalTextSummary(
            code=info["code"],
            name=info["name"],
            version=str(info["year"]),
            status="in_force",
            effective_from=info["effective_date"],
        )
        for info in OHADA_CATALOGUE.values()
    ]


async def get_version(act_code: str) -> dict[str, Any]:
    """Retrieve revision history and chronological versions of a legal text."""
    act = await corpus_client.get_act(act_code=act_code)
    return {
        "act_code": act.code,
        "act_name": act.name,
        "current_version": str(act.year),
        "effective_date": act.effective_date,
        "history": [
            {
                "version": str(act.year),
                "status": "in_force",
                "effective_from": act.effective_date,
                "publication": act.official_source.publication,
            }
        ],
    }


async def get_provision_at_date(act_code: str, article_reference: str, target_date: str) -> TemporalApplicabilityResult:
    """Check applicability metadata without duplicating the full article text."""
    try:
        date.fromisoformat(target_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("target_date doit respecter le format YYYY-MM-DD.") from exc
    article = await get_article(act_code=act_code, article_reference=article_reference)
    is_applicable = bool(
        (not article.effective_from or target_date >= article.effective_from)
        and (not article.effective_until or target_date <= article.effective_until)
    )
    return TemporalApplicabilityResult(
        act_code=article.act_code,
        article_reference=article.article_reference,
        target_date=target_date,
        indexed_version=article.version,
        is_applicable=is_applicable,
        status_at_date="in_force" if is_applicable else "not_applicable",
        effective_from=article.effective_from,
        effective_until=article.effective_until,
        limitation=(
            "Contrôle limité à la période d'effet de la version indexée ; "
            "aucun libellé historique remplacé n'est reconstitué."
        ),
    )


async def verify_citation(citation_text: str) -> CitationVerificationResult:
    """Verify validity, existence and accuracy of an OHADA legal citation."""
    citation_text = citation_text.strip()
    if not citation_text:
        raise ValueError("La citation ne peut pas être vide.")
    if len(citation_text) > settings.MAX_CITATION_LENGTH:
        raise ValueError(
            f"La citation dépasse la limite de {settings.MAX_CITATION_LENGTH} caractères."
        )
    return await corpus_client.verify_citation(citation_text=citation_text)
