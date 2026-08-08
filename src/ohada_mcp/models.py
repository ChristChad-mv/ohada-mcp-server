"""
Pydantic Domain Models for OHADA MCP Legal API.
"""

from pydantic import BaseModel, Field


class OfficialSource(BaseModel):
    """Official publication source metadata for an OHADA text or article."""

    publisher: str = Field(description="Publishing authority (e.g., Secrétariat Permanent de l'OHADA)")
    publication: str = Field(description="Official Gazette or publication reference")
    adopted_at: str | None = Field(default=None, description="Date of adoption (YYYY-MM-DD)")
    published_at: str | None = Field(default=None, description="Date of publication in Official Gazette (YYYY-MM-DD)")
    effective_from: str | None = Field(default=None, description="Date of entry into force (YYYY-MM-DD)")
    url: str | None = Field(default=None, description="Official web reference URL")


class HierarchyContext(BaseModel):
    """Structural location context within a legal code."""

    part: str | None = Field(default=None, description="Part name or number")
    book: str | None = Field(default=None, description="Book name or number")
    title: str | None = Field(default=None, description="Title name or number")
    chapter: str | None = Field(default=None, description="Chapter name or number")
    section: str | None = Field(default=None, description="Section name or number")
    subsection: str | None = Field(default=None, description="Subsection name or number")
    paragraph: str | None = Field(default=None, description="Paragraph name or number")
    full_path: str = Field(description="Full hierarchy path string")


class LegalArticle(BaseModel):
    """Canonical Normative Legal Article object."""

    act_code: str = Field(description="Unique code of the Uniform Act (e.g. AUDCG, AUSCGIE)")
    act_name: str = Field(description="Short name of the Act")
    article_reference: str = Field(description="Article reference string (e.g. '16', '13 bis', '655-1', '44 ter')")
    version: str = Field(description="Promulgation year or version tag (e.g. '2010', '2014')")
    status: str = Field(default="in_force", description="Current legal status: 'in_force', 'repealed', 'amended'")
    effective_from: str | None = Field(default=None, description="Enforcement start date (YYYY-MM-DD)")
    effective_until: str | None = Field(default=None, description="Enforcement end date if repealed (YYYY-MM-DD)")
    hierarchy_context: HierarchyContext = Field(description="Structural location context")
    text: str = Field(description="Complete verbatim normative text of the article")
    official_source: OfficialSource = Field(description="Official publication source")


class ArticleLocator(BaseModel):
    """Exact article identifier used by bounded batch retrieval."""

    act_code: str = Field(description="Canonical act code")
    article_reference: str = Field(description="Exact article reference")


class ArticleLookupError(ArticleLocator):
    """Non-fatal lookup error within an article batch."""

    error: str = Field(description="Public lookup error")


class ArticleBatch(BaseModel):
    """Bounded full-text response for several exact provisions."""

    requested_count: int
    result_count: int
    articles: list[LegalArticle] = Field(default_factory=list)
    errors: list[ArticleLookupError] = Field(default_factory=list)


class LegalAct(BaseModel):
    """Canonical Normative Legal Act object."""

    code: str = Field(description="Unique code of the Uniform Act")
    name: str = Field(description="Short name of the Act")
    full_name: str = Field(description="Full official title of the Act")
    year: int = Field(description="Year of adoption/revision")
    effective_date: str = Field(description="Date of entry into force (YYYY-MM-DD)")
    description: str = Field(description="Summary scope and objective of the Act")
    total_articles: int = Field(default=0, description="Total number of articles in the Act")
    official_source: OfficialSource = Field(description="Official publication source")


class LegalTextSummary(BaseModel):
    """Compact catalogue entry used for tool discovery."""

    code: str = Field(description="Canonical code of the legal text")
    name: str = Field(description="Short name of the legal text")
    version: str = Field(description="Currently indexed version or adoption year")
    status: str = Field(default="in_force", description="Status of the indexed version")
    effective_from: str | None = Field(default=None, description="Entry-into-force date")


class SearchResultItem(BaseModel):
    """Item in a legal search result set."""

    rank: int = Field(description="Rank position in search results")
    act_code: str = Field(description="Code of the matching Act")
    article_reference: str | None = Field(default=None, description="Article reference if identified")
    hierarchy_path: str = Field(description="Hierarchy path of the matching passage")
    snippet: str = Field(description="Short discovery excerpt; retrieve the full article with get_article")


class SearchResults(BaseModel):
    """Container for search results."""

    query: str = Field(description="Original search query")
    result_count: int = Field(description="Number of distinct ranked results returned")
    act_filter: str | None = Field(default=None, description="Act filter applied if any")
    results: list[SearchResultItem] = Field(default_factory=list, description="Ranked list of search results")


class CitationVerificationResult(BaseModel):
    """Result of an OHADA legal citation verification."""

    citation_text: str = Field(description="Original citation string submitted")
    is_valid: bool = Field(description="True if the citation exists in the canonical OHADA legal framework")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    canonical_citation: str | None = Field(default=None, description="Normalized canonical citation if found")
    act_code: str | None = Field(default=None, description="Matched canonical act code")
    article_reference: str | None = Field(default=None, description="Matched canonical article reference")
    version: str | None = Field(default=None, description="Version containing the matched article")
    status: str | None = Field(default=None, description="Status of the matched indexed provision")
    official_source_url: str | None = Field(default=None, description="Official source URL for the matched act")
    explanation: str = Field(description="Detailed verification outcome explanation")


class TemporalApplicabilityResult(BaseModel):
    """Lightweight applicability result for the currently indexed version."""

    act_code: str
    article_reference: str
    target_date: str
    indexed_version: str
    is_applicable: bool
    status_at_date: str
    effective_from: str | None = None
    effective_until: str | None = None
    limitation: str = Field(description="Explicit limitation: the service does not reconstruct superseded wording")
