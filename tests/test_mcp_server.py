"""
Integration Tests for OHADA MCPServer (SDK v2).
"""

import pytest
from ohada_mcp.models import LegalArticle
from ohada_mcp.server import (
    get_act,
    get_article,
    get_articles,
    get_provision_at_date,
    get_version,
    list_legal_texts,
    mcp,
    search_ohada_law,
    verify_citation,
)


@pytest.mark.asyncio
async def test_mcp_server_instantiation():
    assert mcp.name == "OHADA MCP"
    assert "Created by Christ Chad" in mcp.instructions


@pytest.mark.asyncio
async def test_mcp_tools_registration():
    # Verify search_ohada_law, get_article, etc. are registered
    tools = [
        search_ohada_law,
        get_article,
        get_articles,
        get_act,
        list_legal_texts,
        get_version,
        get_provision_at_date,
        verify_citation,
    ]
    for tool in tools:
        assert callable(tool)


@pytest.mark.asyncio
async def test_mcp_get_article_tool():
    art = await get_article(act_code="AUDCG", article_reference="16")
    assert isinstance(art, LegalArticle)
    assert art.article_reference == "16"


@pytest.mark.asyncio
async def test_mcp_list_texts_tool():
    acts = await list_legal_texts()
    assert isinstance(acts, list)
    assert len(acts) >= 11


@pytest.mark.asyncio
async def test_mcp_contracts_are_explicit_and_read_only():
    tools = {tool.name: tool for tool in await mcp.list_tools()}

    assert len(tools) == 8
    assert "extraits courts" in tools["search_ohada_law"].description
    assert "Ne pas appeler" in tools["verify_citation"].description
    assert tools["get_article"].annotations.readOnlyHint is True
    assert tools["get_articles"].annotations.idempotentHint is True
