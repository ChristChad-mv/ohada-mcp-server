"""Deterministic final-answer guard for citations backed by retrieved articles."""

from __future__ import annotations

import re
import unicodedata

from ohada_mcp.catalog import OHADA_CATALOGUE

_REFERENCE = r"\d+(?:[-.]\d+)*(?:\s+(?:bis|ter|quater))?"
_CODES = "|".join(re.escape(code) for code in sorted(OHADA_CATALOGUE, key=len, reverse=True))
_CITATION_RE = re.compile(
    rf"(?:article|art\.?)\s*({_REFERENCE})"
    rf"(?:\s*,?\s*alin[ée]as?\s+[0-9,\set]+)?\s*"
    rf"(?:de\s+l['’]\s*)?({_CODES})",
    re.IGNORECASE,
)
_NON_ASSERTIVE_MARKERS = (
    "n existe pas",
    "n a pas ete retrouve",
    "non retrouve",
    "non resolu",
    "introuvable",
)


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def retrieved_citations(tool_calls: list[dict]) -> set[tuple[str, str]]:
    """Return exact provisions whose complete text was retrieved successfully."""
    citations: set[tuple[str, str]] = set()
    for call in tool_calls:
        output = call.get("output")
        if not isinstance(output, dict):
            continue
        articles = output.get("articles") if call.get("tool") == "get_articles" else [output]
        if not isinstance(articles, list):
            continue
        for article in articles:
            if not isinstance(article, dict) or not article.get("text"):
                continue
            code = str(article.get("act_code", "")).upper().strip()
            reference = str(article.get("article_reference", "")).lower().strip()
            if code in OHADA_CATALOGUE and reference:
                citations.add((code, reference))
    return citations


def unsupported_citations(answer: str, tool_calls: list[dict]) -> list[str]:
    """Find affirmative citations absent from successful full-text retrievals."""
    allowed = retrieved_citations(tool_calls)
    unsupported: list[str] = []
    for match in _CITATION_RE.finditer(answer):
        reference = match.group(1).lower().strip()
        code = match.group(2).upper().strip()
        line_start = answer.rfind("\n", 0, match.start()) + 1
        line_end = answer.find("\n", match.end())
        line = answer[line_start : line_end if line_end >= 0 else len(answer)]
        if any(marker in _normalize(line) for marker in _NON_ASSERTIVE_MARKERS):
            continue
        citation = (code, reference)
        label = f"Article {reference} {code}"
        if citation not in allowed and label not in unsupported:
            unsupported.append(label)
    return unsupported


def remove_unsupported_blocks(answer: str, citations: list[str]) -> str:
    """Fail closed if a correction model still emits an unsupported provision."""
    blocks = re.split(r"\n\s*\n", answer)
    kept = [block for block in blocks if not any(_normalize(citation) in _normalize(block) for citation in citations)]
    cleaned = "\n\n".join(block for block in kept if block.strip()).strip()
    notice = (
        "\n\n> Contrôle des sources : une affirmation associée à une référence non "
        "récupérée a été retirée de cette synthèse."
    )
    return f"{cleaned}{notice}".strip()
