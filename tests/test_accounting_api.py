"""Hermetic contract tests for the SYSCOHADA MCP domain."""

import sqlite3

import pytest
from ohada_mcp import accounting_api
from ohada_mcp.models import (
    SyscohadaAccountContext,
    SyscohadaPassageBatch,
    SyscohadaSearchResults,
)


@pytest.mark.asyncio
async def test_search_then_retrieve_full_syscohada_passage():
    search = await accounting_api.search_syscohada(
        "subventions investissement compte 14",
        max_results=2,
    )

    assert isinstance(search, SyscohadaSearchResults)
    assert search.result_count == 2
    assert search.results[0].account_code == "14"
    assert len(search.results[0].snippet) < len(
        (await accounting_api.get_syscohada_passages([search.results[0].chunk_id])).passages[0].text
    ) or search.results[0].snippet

    batch = await accounting_api.get_syscohada_passages(
        [item.chunk_id for item in search.results]
    )
    assert isinstance(batch, SyscohadaPassageBatch)
    assert batch.result_count == 2
    assert batch.passages[0].official_source.publisher.startswith("Secrétariat")
    assert batch.passages[0].official_source.effective_from == "2018-01-01"
    assert batch.passages[0].citation.startswith("SYSCOHADA — compte 14, p.")


@pytest.mark.asyncio
async def test_get_complete_syscohada_account_context():
    result = await accounting_api.get_syscohada_account("14")

    assert isinstance(result, SyscohadaAccountContext)
    assert result.account_code == "14"
    assert result.passage_count == 2
    assert {passage.account_subsection for passage in result.passages} == {
        "Commentaires",
        "Fonctionnement",
    }


def test_syscohada_repository_opens_database_read_only():
    with (
        accounting_api.syscohada_client.repository._connect() as connection,
        pytest.raises(sqlite3.OperationalError, match="readonly database"),
    ):
        connection.execute("CREATE TABLE forbidden_write (id INTEGER)")


@pytest.mark.asyncio
async def test_syscohada_inputs_are_bounded_and_validated():
    with pytest.raises(ValueError, match="alphanumérique"):
        await accounting_api.search_syscohada("!?;()")
    with pytest.raises(ValueError, match="32 termes"):
        await accounting_api.search_syscohada(
            " ".join(f"terme{index}" for index in range(33))
        )
    with pytest.raises(ValueError, match="entre 1 et 5"):
        await accounting_api.get_syscohada_passages([])
    with pytest.raises(ValueError, match="2 à 4 chiffres"):
        await accounting_api.get_syscohada_account("14; DROP TABLE chunks")
    with pytest.raises(ValueError, match="max_results"):
        await accounting_api.search_syscohada("compte", max_results=100)
