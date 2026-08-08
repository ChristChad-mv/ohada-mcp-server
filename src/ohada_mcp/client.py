"""
Corpus Backend Client — Interfaces with the private OHADA Corpus Service.

Encapsulates data retrieval and maps raw storage results into canonical
normative legal domain objects (LegalArticle, LegalAct, SearchResults).
"""

import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

from ohada_mcp.catalog import OHADA_CATALOGUE
from ohada_mcp.config import settings
from ohada_mcp.models import (
    CitationVerificationResult,
    HierarchyContext,
    LegalAct,
    LegalArticle,
    OfficialSource,
    SearchResultItem,
    SearchResults,
)
from ohada_mcp.repositories import (
    CorpusRepository,
    RepositoryError,
    SQLiteCorpusRepository,
    StoredChunk,
)

logger = logging.getLogger(__name__)

ACT_TITLE_ALIASES = {
    "TRAITE": ("traite ohada", "traite relatif a l harmonisation"),
    "AUDCG": ("droit commercial general",),
    "AUSCGIE": (
        "droit des societes commerciales et du groupement d interet economique",
        "societes commerciales et gie",
    ),
    "AUPCAP": ("procedures collectives d apurement du passif",),
    "AUS": ("organisation des suretes", "droit des suretes"),
    "AUA": ("droit de l arbitrage",),
    "AUM": ("mediation",),
    "AUDCIF": ("droit comptable et a l information financiere", "syscohada"),
    "AUSCOOP": ("droit des societes cooperatives", "societes cooperatives"),
    "AUCTMR": ("contrats de transport de marchandises par route",),
    "AUPSRVE": (
        "procedures simplifiees de recouvrement et des voies d execution",
        "recouvrement et voies d execution",
    ),
    "REGLEMENT-ARBITRAGE-CCJA": ("reglement d arbitrage ccja",),
    "REGLEMENT-PROCEDURE-CCJA": ("reglement de procedure ccja",),
}


def _normalize_legal_text(value: str) -> str:
    """Normalize accents and punctuation for resilient title recognition."""
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


ARTICLE_PATH_PATTERN = re.compile(
    r"(?:^|>\s*)Article\s+"
    r"(\d+(?:[-.]\d+)*(?:\s+(?:bis|ter|quater))?)"
    r"(?:\s*$|\s*>)",
    re.IGNORECASE,
)
ARTICLE_HEADING_PATTERN = re.compile(r"(?im)^Article\s+(\d+(?:[-.]\d+)*(?:\s+(?:bis|ter|quater))?)\s*$")
BATCH_PATH_PATTERN = re.compile(r"_batch_\d+-\d+$", re.IGNORECASE)
REPEATED_DOCUMENT_HEADER_PATTERN = re.compile(
    r"^(?:ACTE\s+UNIFORME\b.*|Adopté\s+le\b.*|Publié\s+au\s+Journal\s+Officiel\b.*|"
    r"LIVRE\s+[IVXLC]+\s*:.*)$",
    re.IGNORECASE,
)


def _article_reference_from_path(hierarchy_path: str) -> str | None:
    """Return the canonical terminal article reference from a hierarchy path."""
    match = ARTICLE_PATH_PATTERN.search(hierarchy_path)
    return match.group(1).strip().lower() if match else None


def _clean_article_chunk(text: str) -> str:
    """Remove the embedding-only hierarchy prefix from a normative chunk."""
    return re.sub(r"^\[[^\]\n]*\]\s*", "", text).strip()


def _embedded_article_segments(text: str) -> dict[str, str]:
    """Extract articles grouped inside a chunk whose hierarchy is only a section."""
    cleaned = _clean_article_chunk(text)
    headings = list(ARTICLE_HEADING_PATTERN.finditer(cleaned))
    segments: dict[str, str] = {}
    for index, heading in enumerate(headings):
        reference = heading.group(1).strip().lower()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(cleaned)
        body = cleaned[heading.end() : end].strip()
        if body and len(body) > len(segments.get(reference, "")):
            segments[reference] = body
    return segments


def _continuation_prefix_from_path(hierarchy_path: str) -> str:
    """Recover words incorrectly promoted to a hierarchy label by the chunker."""
    if BATCH_PATH_PATTERN.search(hierarchy_path) or _article_reference_from_path(hierarchy_path):
        return ""
    tail = hierarchy_path.rsplit(">", 1)[-1].strip()
    if not tail or re.match(
        r"^(?:partie|livre|titre|chapitre|section|sous-section|paragraphe|acte uniforme)\b",
        tail,
        re.IGNORECASE,
    ):
        return ""
    if tail[:1].islower() or tail.endswith((":", ";")):
        return tail
    return ""


def _clean_batch_continuation(text: str, hierarchy_path: str = "") -> str:
    """Keep only normative text before the first new article in a continuation chunk."""
    cleaned = _clean_article_chunk(text)
    lines = cleaned.splitlines()
    while lines and REPEATED_DOCUMENT_HEADER_PATTERN.match(lines[0].strip()):
        lines.pop(0)
    cleaned = "\n".join(lines).strip()
    next_article = ARTICLE_HEADING_PATTERN.search(cleaned)
    if next_article:
        cleaned = cleaned[: next_article.start()].strip()
    prefix = _continuation_prefix_from_path(hierarchy_path)
    return "\n".join(part for part in (prefix, cleaned) if part)


def _simple_article_number(reference: str | None) -> int | None:
    return int(reference) if reference and reference.isdigit() else None


def _looks_strongly_incomplete(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:un|une|le|la|les|de|des|du|à|au|aux|et|ou|pour|dans|par|sur)\s*$",
            text,
            re.IGNORECASE,
        )
    )


def _infer_unlabelled_article_run(
    candidates: list[StoredChunk],
    article_reference: str,
) -> list[StoredChunk]:
    """Infer a missing integer heading between its immediate numbered neighbours."""
    target = _simple_article_number(article_reference.strip().lower())
    if target is None:
        return []

    rows = sorted(candidates, key=lambda row: row.id)
    inferred_runs: list[list[StoredChunk]] = []
    for index, row in enumerate(rows):
        if _article_reference_from_path(row.hierarchy_path):
            continue
        if _embedded_article_segments(row.text_content):
            continue

        previous_ref = _article_reference_from_path(rows[index - 1].hierarchy_path) if index else None
        next_ref = _article_reference_from_path(rows[index + 1].hierarchy_path) if index + 1 < len(rows) else None
        if _simple_article_number(previous_ref) == target - 1 and _simple_article_number(next_ref) == target + 1:
            inferred_runs.append([row])

    return max(
        inferred_runs,
        key=lambda run: sum(len(_clean_article_chunk(row.text_content)) for row in run),
        default=[],
    )


def _following_article_continuations(
    candidates: list[StoredChunk],
    article_rows: list[StoredChunk],
    article_reference: str,
) -> list[str]:
    """Recover article text orphaned or mislabelled by PDF layout chunking."""
    if not article_rows:
        return []

    rows_by_id = {row.id: row for row in candidates}
    next_id = article_rows[-1].id + 1
    continuations: list[str] = []
    assembled = "\n".join(_clean_article_chunk(row.text_content) for row in article_rows)
    target_number = _simple_article_number(article_reference.strip().lower())
    while (row := rows_by_id.get(next_id)) is not None:
        cleaned_row = _clean_article_chunk(row.text_content)
        row_reference = _article_reference_from_path(row.hierarchy_path)
        embedded_references = _embedded_article_segments(row.text_content)
        following_row = rows_by_id.get(next_id + 1)
        following_reference = _article_reference_from_path(following_row.hierarchy_path) if following_row else None

        at_batch_boundary = bool(BATCH_PATH_PATTERN.search(row.hierarchy_path))
        between_current_and_next = (
            row_reference is None
            and not embedded_references
            and target_number is not None
            and _simple_article_number(following_reference) == target_number + 1
        )
        misplaced_continuation = (
            row_reference is not None
            and target_number is not None
            and _simple_article_number(following_reference) == target_number + 1
            and (_looks_strongly_incomplete(assembled) or cleaned_row[:1].islower())
        )
        if not (
            at_batch_boundary
            or between_current_and_next
            or misplaced_continuation
            or (_looks_strongly_incomplete(assembled) and row_reference is None)
        ):
            break
        if continuation := _clean_batch_continuation(row.text_content, row.hierarchy_path):
            continuations.append(continuation)
            assembled = f"{assembled}\n{continuation}"
        if row_reference or ARTICLE_HEADING_PATTERN.search(cleaned_row):
            break
        next_id += 1
    return continuations


def _build_search_snippet(text: str, query: str, max_chars: int) -> str:
    """Build a bounded discovery excerpt around the first meaningful query term."""
    cleaned = _clean_article_chunk(text)
    if len(cleaned) <= max_chars:
        return cleaned

    terms = [term for term in re.findall(r"\w+", query, re.UNICODE) if len(term) >= 4]
    positions = [match.start() for term in terms if (match := re.search(re.escape(term), cleaned, re.IGNORECASE))]
    anchor = min(positions) if positions else 0
    start = max(0, anchor - max_chars // 3)
    end = min(len(cleaned), start + max_chars)
    start = max(0, end - max_chars)
    excerpt = cleaned[start:end].strip()
    return f"{'… ' if start else ''}{excerpt}{' …' if end < len(cleaned) else ''}"


def _select_embedded_search_segment(text: str, query: str) -> tuple[str | None, str]:
    """Choose the embedded article that best matches the query terms."""
    segments = _embedded_article_segments(text)
    if not segments:
        return None, text

    terms = [term.lower() for term in re.findall(r"\w+", query, re.UNICODE) if len(term) >= 4]

    def relevance(item: tuple[str, str]) -> tuple[int, int]:
        _, body = item
        body_lower = body.lower()
        return sum(body_lower.count(term) for term in terms), len(body)

    reference, body = max(segments.items(), key=relevance)
    return reference, body


def _count_canonical_articles(rows: list[StoredChunk]) -> int:
    references: set[str] = set()
    for row in rows:
        if reference := _article_reference_from_path(row.hierarchy_path):
            references.add(reference)
        references.update(_embedded_article_segments(row.text_content))
    return len(references)


def _select_complete_article_run(
    candidates: list[StoredChunk],
    article_reference: str,
) -> list[StoredChunk]:
    """Select the most complete contiguous run for an exact article.

    Long provisions are intentionally split into consecutive search chunks.
    Some source files were also ingested more than once, so concatenating every
    matching row would duplicate whole provisions. We therefore reconstruct
    contiguous rows sharing the exact hierarchy path, then select the run with
    the greatest normative-text length.
    """
    exact_reference = article_reference.strip().lower()
    matching = sorted(
        (row for row in candidates if _article_reference_from_path(row.hierarchy_path) == exact_reference),
        key=lambda row: row.id,
    )
    if not matching:
        return []

    runs: list[list[StoredChunk]] = []
    for row in matching:
        if runs and row.id == runs[-1][-1].id + 1 and row.hierarchy_path == runs[-1][-1].hierarchy_path:
            runs[-1].append(row)
        else:
            runs.append([row])

    def run_quality(run: list[StoredChunk]) -> tuple[int, int, int]:
        text_length = sum(len(_clean_article_chunk(row.text_content)) for row in run)
        return text_length, len(run), -run[0].id

    return max(runs, key=run_quality)


def _select_article_rows(
    candidates: list[StoredChunk],
    article_reference: str,
) -> list[StoredChunk]:
    """Choose the most complete exact or safely inferred row run for an article."""
    exact = _select_complete_article_run(candidates, article_reference)
    inferred = _infer_unlabelled_article_run(candidates, article_reference)
    choices = [rows for rows in (exact, inferred) if rows]

    def assembled_length(rows: list[StoredChunk]) -> int:
        exact_length = sum(len(_clean_article_chunk(row.text_content)) for row in rows)
        continuation_length = sum(
            len(text) for text in _following_article_continuations(candidates, rows, article_reference)
        )
        return exact_length + continuation_length

    return max(choices, key=assembled_length, default=[])


# The production corpus is injected explicitly. A relative development path is
# resolved from the process working directory; no machine-specific fallback is
# allowed in public code.
DEFAULT_DB_PATH = settings.OHADA_DB_PATH.expanduser()
if not DEFAULT_DB_PATH.is_absolute():
    DEFAULT_DB_PATH = Path.cwd() / DEFAULT_DB_PATH


class CorpusBackendClient:
    """Client communicating with the OHADA Legal Corpus backend."""

    def __init__(
        self,
        db_path: str | None = None,
        repository: CorpusRepository | None = None,
    ):
        self.repository = repository or SQLiteCorpusRepository(db_path or DEFAULT_DB_PATH)

    @property
    def db_path(self) -> Path:
        """Compatibility path used by health checks and hermetic test injection."""
        return self.repository.db_path

    @db_path.setter
    def db_path(self, value: str | Path) -> None:
        self.repository.db_path = Path(value)

    def _parse_hierarchy(self, hierarchy_path: str) -> HierarchyContext:
        """Parse hierarchy string into structured HierarchyContext."""
        parts = [p.strip() for p in hierarchy_path.split(">") if p.strip()]

        context = {
            "part": None,
            "book": None,
            "title": None,
            "chapter": None,
            "section": None,
            "subsection": None,
            "paragraph": None,
            "full_path": hierarchy_path,
        }

        unclassified = []
        for part in parts:
            p_lower = part.lower()
            if "partie" in p_lower:
                context["part"] = part
            elif "livre" in p_lower:
                context["book"] = part
            elif "titre" in p_lower:
                context["title"] = part
            elif "chapitre" in p_lower:
                context["chapter"] = part
            elif "sous-section" in p_lower:
                context["subsection"] = part
            elif "section" in p_lower:
                context["section"] = part
            elif "paragraphe" in p_lower or "§" in p_lower:
                context["paragraph"] = part
            elif not p_lower.startswith("article"):
                unclassified.append(part)

        if unclassified:
            if not context["section"]:
                context["section"] = " > ".join(unclassified)
            elif not context["chapter"]:
                context["chapter"] = " > ".join(unclassified)

        return HierarchyContext(**context)

    def _get_act_info(self, act_code: str) -> dict[str, Any]:
        if not isinstance(act_code, str):
            raise TypeError("Le code de l'acte doit être une chaîne de caractères.")
        code_upper = act_code.upper().strip()
        if code_upper not in OHADA_CATALOGUE:
            supported = ", ".join(sorted(OHADA_CATALOGUE))
            raise ValueError(f"Code d'acte OHADA inconnu: {act_code!r}. Codes disponibles: {supported}.")
        return OHADA_CATALOGUE[code_upper]

    async def list_acts(self) -> list[LegalAct]:
        """List all canonical OHADA legal acts in the catalogue."""
        acts = []

        for info in OHADA_CATALOGUE.values():
            article_count = _count_canonical_articles(self.repository.chunks_for_document(info["file"]))

            acts.append(
                LegalAct(
                    code=info["code"],
                    name=info["name"],
                    full_name=info["full_name"],
                    year=info["year"],
                    effective_date=info["effective_date"],
                    description=info["description"],
                    total_articles=article_count,
                    official_source=OfficialSource(
                        publisher=info["publisher"],
                        publication=info["publication"],
                        adopted_at=info.get("adopted_at"),
                        published_at=info.get("published_at"),
                        effective_from=info.get("effective_date"),
                        url=info["url"],
                    ),
                )
            )

        return acts

    async def get_act(self, act_code: str) -> LegalAct:
        """Get details for a specific OHADA Act."""
        info = self._get_act_info(act_code)
        article_count = _count_canonical_articles(self.repository.chunks_for_document(info["file"]))

        return LegalAct(
            code=info["code"],
            name=info["name"],
            full_name=info["full_name"],
            year=info["year"],
            effective_date=info["effective_date"],
            description=info["description"],
            total_articles=article_count,
            official_source=OfficialSource(
                publisher=info["publisher"],
                publication=info["publication"],
                adopted_at=info.get("adopted_at"),
                published_at=info.get("published_at"),
                effective_from=info.get("effective_date"),
                url=info["url"],
            ),
        )

    async def get_article(self, act_code: str, article_reference: str) -> LegalArticle:
        """Fetch canonical normative LegalArticle by act code and reference string."""
        info = self._get_act_info(act_code)
        file_name = info["file"]
        art_ref_clean = str(article_reference).strip()

        # Read the whole source so a provision cut exactly at an ingestion batch
        # boundary can recover its immediately following unclassified chunk.
        # Exact reference parsing still prevents confusing 16 with 160/161.
        candidates = self.repository.chunks_for_document(file_name)
        article_rows = _select_article_rows(candidates, art_ref_clean)
        if article_rows:
            resolved_reference = _article_reference_from_path(article_rows[0].hierarchy_path)
            hierarchy_path = article_rows[0].hierarchy_path
            if resolved_reference != art_ref_clean.lower():
                hierarchy_path = f"{hierarchy_path} > Article {art_ref_clean}"
            text_parts = [cleaned for row in article_rows if (cleaned := _clean_article_chunk(row.text_content))]
            text_parts.extend(_following_article_continuations(candidates, article_rows, art_ref_clean))
            text_clean = "\n".join(text_parts)
        else:
            # Some short consecutive provisions were ingested inside one
            # section-level chunk. Resolve an exact line heading and isolate its
            # body without leaking the neighbouring article.
            embedded_matches = []
            for row in candidates:
                segment = _embedded_article_segments(row.text_content).get(art_ref_clean.lower())
                if segment:
                    embedded_matches.append((len(segment), -row.id, row, segment))

            if not embedded_matches:
                raise ValueError(f"Article {article_reference} introuvable dans l'Acte {act_code}.")
            _, _, selected_row, text_clean = max(embedded_matches, key=lambda item: (item[0], item[1]))
            hierarchy_path = f"{selected_row.hierarchy_path} > Article {art_ref_clean}"

        return LegalArticle(
            act_code=info["code"],
            act_name=info["name"],
            article_reference=art_ref_clean,
            version=str(info["year"]),
            status="in_force",
            effective_from=info["effective_date"],
            effective_until=None,
            hierarchy_context=self._parse_hierarchy(hierarchy_path),
            text=text_clean,
            official_source=OfficialSource(
                publisher=info["publisher"],
                publication=info["publication"],
                adopted_at=info.get("adopted_at"),
                published_at=info.get("published_at"),
                effective_from=info.get("effective_date"),
                url=info["url"],
            ),
        )

    async def search(self, query: str, limit: int = 5, act_filter: str | None = None) -> SearchResults:
        """Perform storage-neutral legal discovery over the OHADA corpus."""

        target_file = None
        if act_filter:
            act_info = self._get_act_info(act_filter)
            target_file = act_info["file"]

        rows = self.repository.search_chunks(
            query,
            candidate_limit=max(limit * 20, 100),
            document_name=target_file,
        )

        results_items = []
        seen_results: set[tuple[str, str]] = set()
        for row in rows:
            hierarchy_path = row.hierarchy_path
            doc_name = row.document_name

            # Detect act_code from doc_name
            act_code = "OHADA"
            for k, v in OHADA_CATALOGUE.items():
                if v["file"] == doc_name:
                    act_code = k
                    break

            # Extract article ref if present
            art_ref = _article_reference_from_path(hierarchy_path)
            searchable_text = row.text_content
            if art_ref is None:
                art_ref, searchable_text = _select_embedded_search_segment(row.text_content, query)

            result_key = (act_code, art_ref or f"path:{hierarchy_path}")
            if result_key in seen_results:
                continue
            seen_results.add(result_key)

            results_items.append(
                SearchResultItem(
                    rank=len(results_items) + 1,
                    act_code=act_code,
                    article_reference=art_ref,
                    hierarchy_path=hierarchy_path,
                    snippet=_build_search_snippet(searchable_text, query, settings.SEARCH_SNIPPET_LENGTH),
                )
            )
            if len(results_items) >= limit:
                break

        return SearchResults(
            query=query,
            result_count=len(results_items),
            act_filter=act_filter,
            results=results_items,
        )

    async def verify_citation(self, citation_text: str) -> CitationVerificationResult:
        """Verify validity of an OHADA legal citation."""
        article_match = re.search(
            r"(?:article|art\.?)\s*(\d+(?:[-.]\d+)*(?:\s+(?:bis|ter|quater))?)",
            citation_text,
            re.IGNORECASE,
        )

        if article_match:
            art_ref = article_match.group(1)
            normalized = _normalize_legal_text(citation_text)
            act_code = None

            # Prefer an explicit canonical code wherever it occurs.
            for code in sorted(OHADA_CATALOGUE, key=len, reverse=True):
                if re.search(rf"(?<![A-Z0-9-]){re.escape(code)}(?![A-Z0-9-])", citation_text, re.IGNORECASE):
                    act_code = code
                    break

            # Otherwise recognize the official long title or a controlled alias.
            if act_code is None:
                for code, aliases in ACT_TITLE_ALIASES.items():
                    if any(alias in normalized for alias in aliases):
                        act_code = code
                        break

            if act_code is None:
                return CitationVerificationResult(
                    citation_text=citation_text,
                    is_valid=False,
                    confidence=0.0,
                    explanation="Article reconnu, mais le texte OHADA cité n'a pas pu être identifié.",
                )

            try:
                article = await self.get_article(act_code, art_ref)
                return CitationVerificationResult(
                    citation_text=citation_text,
                    is_valid=True,
                    confidence=1.0,
                    canonical_citation=f"Article {article.article_reference} {article.act_code}",
                    act_code=article.act_code,
                    article_reference=article.article_reference,
                    version=article.version,
                    status=article.status,
                    official_source_url=article.official_source.url,
                    explanation=f"Citation valide. {article.act_code} Article {article.article_reference} identifié.",
                )
            except (FileNotFoundError, RepositoryError, ValueError):
                return CitationVerificationResult(
                    citation_text=citation_text,
                    is_valid=False,
                    confidence=0.5,
                    explanation=f"Référence {act_code} Article {art_ref} non trouvée dans le corpus indexé.",
                )

        return CitationVerificationResult(
            citation_text=citation_text,
            is_valid=False,
            confidence=0.0,
            explanation="Impossible de reconnaître une structure de citation OHADA valide (ex: 'Article 16 AUDCG').",
        )

    async def get_act_structure(self, act_code: str) -> dict[str, Any]:
        info = self._get_act_info(act_code)
        paths = self.repository.structure_paths(info["file"])
        return {
            "act_code": info["code"],
            "act_name": info["name"],
            "year": info["year"],
            "structure_sample": paths,
        }


# Default singleton instance
corpus_client = CorpusBackendClient()
