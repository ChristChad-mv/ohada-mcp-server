"""
OHADA MCP Server — Streamable HTTP server built with the official MCP Python SDK.
Exposes normative legal tools and URI resources for OHADA law.

Author: Christ Chad
License: MIT
"""

import logging
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from ohada_mcp import accounting_api, legal_api
from ohada_mcp.config import settings
from ohada_mcp.middleware import PrivacyRateLimitMiddleware, SecurityHeadersMiddleware
from ohada_mcp.models import (
    ArticleBatch,
    ArticleLocator,
    CitationVerificationResult,
    LegalAct,
    LegalArticle,
    LegalTextSummary,
    SearchResults,
    SyscohadaAccountContext,
    SyscohadaPassageBatch,
    SyscohadaSearchResults,
    TemporalApplicabilityResult,
)
from ohada_mcp.tool_contracts import TOOL_DESCRIPTIONS

logger = logging.getLogger("ohada-mcp")

# Explicit host/origin allowlists keep the service compatible with reverse
# proxies without disabling the SDK's transport protections globally.
transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=settings.ENABLE_DNS_REBINDING_PROTECTION,
    allowed_hosts=settings.ALLOWED_HOSTS,
    allowed_origins=settings.ALLOWED_ORIGINS,
)

mcp = FastMCP(
    name="OHADA MCP",
    instructions=(
        "Independent Open Legal Infrastructure for OHADA Law (17 Member States). "
        "Created by Christ Chad. Provides normative legal retrieval, article resolution, "
        "temporal applicability checks, and legal citation verification."
    ),
    host=settings.HOST,
    port=settings.PORT,
    streamable_http_path=settings.MCP_PATH,
    stateless_http=settings.STATELESS_HTTP,
    json_response=settings.JSON_RESPONSE,
    max_request_body_size=settings.MAX_REQUEST_BODY_SIZE,
    transport_security=transport_security,
)

# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

READ_ONLY_TOOL = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


@mcp.tool(description=TOOL_DESCRIPTIONS["search_ohada_law"], annotations=READ_ONLY_TOOL)
async def search_ohada_law(
    query: str, max_results: int = 5, act_filter: str | None = None, ctx: Context | None = None
) -> SearchResults:
    """Recherche textuelle dans les textes juridiques OHADA indexés.

    Interroge le dépôt de corpus configuré et retourne des candidats compacts.

    Args:
        query: Question ou concepts juridiques en français (ex: 'délai de prescription créance commerciale')
        max_results: Nombre maximal d'articles à retourner (1 à 10, défaut: 5)
        act_filter: Filtrer optionnellement par code d'Acte (ex: 'AUDCG', 'AUSCGIE', 'AUPCAP')
    """
    return await legal_api.search_ohada_law(query=query, max_results=max_results, act_filter=act_filter)


@mcp.tool(description=TOOL_DESCRIPTIONS["get_article"], annotations=READ_ONLY_TOOL)
async def get_article(act_code: str, article_reference: str, ctx: Context | None = None) -> LegalArticle:
    """Récupère le texte normatif complet et le contexte d'un article OHADA.

    Supporte les références complexes d'articles (ex: '16', '13 bis', '655-1', '44 ter').

    Args:
        act_code: Code de l'Acte Uniforme (ex: 'AUDCG', 'AUSCGIE', 'AUPCAP', 'AUS', 'AUA')
        article_reference: Numéro ou référence exacte de l'article (ex: '16', '655-1', '27 ter')
    """
    return await legal_api.get_article(act_code=act_code, article_reference=article_reference)


@mcp.tool(description=TOOL_DESCRIPTIONS["get_articles"], annotations=READ_ONLY_TOOL)
async def get_articles(articles: list[ArticleLocator], ctx: Context | None = None) -> ArticleBatch:
    """Récupère en une fois deux à cinq articles exacts et complets."""
    return await legal_api.get_articles(articles=articles)


@mcp.tool(description=TOOL_DESCRIPTIONS["get_act"], annotations=READ_ONLY_TOOL)
async def get_act(act_code: str, ctx: Context | None = None) -> LegalAct:
    """Récupère les métadonnées et la structure hiérarchique d'un Acte Uniforme OHADA.

    Args:
        act_code: Code de l'Acte Uniforme (ex: 'AUDCG', 'AUSCGIE', 'AUPCAP')
    """
    return await legal_api.get_act(act_code=act_code)


@mcp.tool(description=TOOL_DESCRIPTIONS["list_legal_texts"], annotations=READ_ONLY_TOOL)
async def list_legal_texts(ctx: Context | None = None) -> list[LegalTextSummary]:
    """Catalogue complet de tous les textes juridiques OHADA promulgués et indexés."""
    return await legal_api.list_legal_texts()


@mcp.tool(description=TOOL_DESCRIPTIONS["get_version"], annotations=READ_ONLY_TOOL)
async def get_version(act_code: str, ctx: Context | None = None) -> dict[str, Any]:
    """Récupère l'historique des révisions et versions chronologiques d'un texte OHADA.

    Args:
        act_code: Code de l'Acte Uniforme (ex: 'AUDCG', 'AUSCGIE')
    """
    return await legal_api.get_version(act_code=act_code)


@mcp.tool(description=TOOL_DESCRIPTIONS["get_provision_at_date"], annotations=READ_ONLY_TOOL)
async def get_provision_at_date(
    act_code: str, article_reference: str, target_date: str, ctx: Context | None = None
) -> TemporalApplicabilityResult:
    """Contrôle l'applicabilité de la version indexée à une date donnée.

    Args:
        act_code: Code de l'Acte Uniforme (ex: 'AUDCG', 'AUSCGIE')
        article_reference: Numéro/référence de l'article (ex: '16')
        target_date: Date d'application recherchée au format YYYY-MM-DD (ex: '2018-03-12')
    """
    return await legal_api.get_provision_at_date(
        act_code=act_code, article_reference=article_reference, target_date=target_date
    )


@mcp.tool(description=TOOL_DESCRIPTIONS["verify_citation"], annotations=READ_ONLY_TOOL)
async def verify_citation(citation_text: str, ctx: Context | None = None) -> CitationVerificationResult:
    """Contrôle la validité, l'existence et l'exactitude d'une citation juridique OHADA.

    Args:
        citation_text: Texte de la citation à vérifier (ex: 'Article 16 AUDCG' ou 'Article 655-1 AUSCGIE')
    """
    return await legal_api.verify_citation(citation_text=citation_text)


@mcp.tool(description=TOOL_DESCRIPTIONS["search_syscohada"], annotations=READ_ONLY_TOOL)
async def search_syscohada(
    query: str,
    max_results: int = 5,
    account_filter: str | None = None,
    class_filter: str | None = None,
    ctx: Context | None = None,
) -> SyscohadaSearchResults:
    """Découvre des passages dans la publication officielle SYSCOHADA."""
    return await accounting_api.search_syscohada(
        query=query,
        max_results=max_results,
        account_filter=account_filter,
        class_filter=class_filter,
    )


@mcp.tool(description=TOOL_DESCRIPTIONS["get_syscohada_passages"], annotations=READ_ONLY_TOOL)
async def get_syscohada_passages(
    chunk_ids: list[int], ctx: Context | None = None
) -> SyscohadaPassageBatch:
    """Récupère le texte complet de passages SYSCOHADA exacts."""
    return await accounting_api.get_syscohada_passages(chunk_ids=chunk_ids)


@mcp.tool(description=TOOL_DESCRIPTIONS["get_syscohada_account"], annotations=READ_ONLY_TOOL)
async def get_syscohada_account(
    account_code: str, ctx: Context | None = None
) -> SyscohadaAccountContext:
    """Récupère tous les passages officiels d'un compte SYSCOHADA exact."""
    return await accounting_api.get_syscohada_account(account_code=account_code)


# ---------------------------------------------------------------------------
# MCP Resources URIs (RFC 6570)
# ---------------------------------------------------------------------------


@mcp.resource("ohada://texts")
async def resource_all_texts() -> list[dict[str, Any]]:
    """Catalogue complet des textes juridiques OHADA disponibles."""
    acts = await legal_api.list_legal_texts()
    return [act.model_dump(mode="json") for act in acts]


@mcp.resource("ohada://act/{code}")
async def resource_act_structure(code: str) -> dict[str, Any]:
    """Structure hiérarchique et métadonnées d'un Acte Uniforme OHADA."""
    from ohada_mcp.client import corpus_client

    return await corpus_client.get_act_structure(code)


@mcp.resource("ohada://act/{code}/article/{article}")
async def resource_article_text(code: str, article: str) -> dict[str, Any]:
    """Texte brut normatif et métadonnées d'un article OHADA."""
    art = await legal_api.get_article(act_code=code, article_reference=article)
    return art.model_dump(mode="json")


@mcp.resource("ohada://act/{code}/versions")
async def resource_act_versions(code: str) -> dict[str, Any]:
    """Historique des versions et révisions d'un Acte Uniforme."""
    return await legal_api.get_version(act_code=code)


# ---------------------------------------------------------------------------
# Server Entrypoint (Streamable HTTP Transport & Cloud Run Readiness)
# ---------------------------------------------------------------------------


async def _health_endpoint(request):
    from starlette.responses import JSONResponse

    from ohada_mcp.accounting_api import syscohada_client
    from ohada_mcp.catalog import OHADA_CATALOGUE
    from ohada_mcp.client import corpus_client

    corpus_ready = corpus_client.db_path.is_file()
    syscohada_ready = syscohada_client.db_path.is_file()
    return JSONResponse(
        {
            "status": "healthy" if corpus_ready else "degraded",
            "service": "OHADA Remote MCP Server",
            "mcp_endpoint": settings.MCP_PATH,
            "corpus_ready": corpus_ready,
            "syscohada_ready": syscohada_ready,
            "texts_count": len(OHADA_CATALOGUE),
            "author": "Christ Chad",
        },
        status_code=200 if corpus_ready else 503,
    )


def main():
    """Main application runner."""
    import os

    import uvicorn
    from starlette.routing import Route

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    port = int(os.environ.get("PORT", settings.PORT))
    host = os.environ.get("HOST", settings.HOST)

    logger.info(f"Démarrage OHADA MCP Server sur {host}:{port}{settings.MCP_PATH}...")

    # Build Streamable HTTP Starlette app from FastMCP
    app = mcp.streamable_http_app()
    app.routes.insert(0, Route("/", _health_endpoint))
    app.routes.insert(0, Route("/health", _health_endpoint))

    app = PrivacyRateLimitMiddleware(
        app,
        enabled=settings.RATE_LIMIT_ENABLED,
        requests=settings.RATE_LIMIT_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
        protected_path=settings.MCP_PATH,
        max_clients=settings.RATE_LIMIT_MAX_CLIENTS,
        trust_proxy_headers=settings.TRUST_PROXY_HEADERS,
        trusted_proxy_hops=settings.TRUSTED_PROXY_HOPS,
    )
    app = SecurityHeadersMiddleware(app)

    # Access logs contain paths and network metadata but no request bodies. We
    # disable them for the public service to minimize retained usage data.
    uvicorn.run(app, host=host, port=port, access_log=False, server_header=False)


if __name__ == "__main__":
    main()
