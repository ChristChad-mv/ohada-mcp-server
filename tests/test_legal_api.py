"""
Unit and Integration Tests for OHADA MCP Legal API.
"""

import json
import sqlite3

import pytest
from ohada_mcp import legal_api
from ohada_mcp.models import CitationVerificationResult, LegalArticle, SearchResults


@pytest.mark.asyncio
async def test_list_legal_texts():
    texts = await legal_api.list_legal_texts()
    assert len(texts) >= 11
    codes = [t.code for t in texts]
    assert "AUDCG" in codes
    assert "AUSCGIE" in codes
    assert "AUPCAP" in codes
    assert "TRAITE" in codes


@pytest.mark.asyncio
async def test_get_act():
    act = await legal_api.get_act("AUDCG")
    assert act.code == "AUDCG"
    assert "Droit Commercial Général" in act.name
    assert act.year == 2010
    assert act.total_articles > 0


@pytest.mark.asyncio
async def test_get_article_standard():
    art = await legal_api.get_article("AUDCG", "16")
    assert isinstance(art, LegalArticle)
    assert art.act_code == "AUDCG"
    assert art.article_reference == "16"
    assert "Prescription" in art.hierarchy_context.full_path
    assert "cinq ans" in art.text.lower()


@pytest.mark.asyncio
async def test_get_articles_batches_full_text_and_isolates_lookup_errors():
    batch = await legal_api.get_articles(
        [
            {"act_code": "AUDCG", "article_reference": "16"},
            {"act_code": "AUSCGIE", "article_reference": "99999"},
        ]
    )

    assert batch.requested_count == 2
    assert batch.result_count == 1
    assert batch.articles[0].article_reference == "16"
    assert "cinq ans" in batch.articles[0].text.lower()
    assert batch.errors[0].article_reference == "99999"


@pytest.mark.asyncio
async def test_get_articles_rejects_unbounded_or_duplicate_batches():
    with pytest.raises(ValueError, match="entre 2 et 5"):
        await legal_api.get_articles([{"act_code": "AUDCG", "article_reference": "16"}])

    with pytest.raises(ValueError, match="dupliquée"):
        await legal_api.get_articles(
            [
                {"act_code": "AUDCG", "article_reference": "16"},
                {"act_code": "audcg", "article_reference": "16"},
            ]
        )


@pytest.mark.asyncio
async def test_get_article_complex_reference():
    # Test article with complex reference string (e.g. 655-1 in AUSCGIE)
    art = await legal_api.get_article("AUSCGIE", "655-1")
    assert isinstance(art, LegalArticle)
    assert art.act_code == "AUSCGIE"
    assert art.article_reference == "655-1"
    assert "Amortissement du capital" in art.hierarchy_context.full_path


@pytest.mark.asyncio
async def test_get_article_reconstructs_all_contiguous_chunks_without_duplicates(
    isolated_test_corpus,
):
    connection = sqlite3.connect(isolated_test_corpus)
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (10, "auscgie", "Article 440", "[Article 440]\nPremier alinéa canonique."),
            (11, "auscgie", "Article 440", "[Article 440]\nDernier alinéa canonique."),
        ],
    )
    # Simulate a second ingestion of the same source. It must not duplicate the
    # returned provision.
    connection.execute(
        "INSERT INTO documents(id, name) VALUES (?, ?)",
        ("auscgie_duplicate", "AUSCGIE-2014_fr.pdf"),
    )
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (20, "auscgie_duplicate", "Article 440", "[Article 440]\nPremier alinéa canonique."),
            (21, "auscgie_duplicate", "Article 440", "[Article 440]\nDernier alinéa canonique."),
        ],
    )
    connection.commit()
    connection.close()

    article = await legal_api.get_article("AUSCGIE", "440")

    assert article.text == "Premier alinéa canonique.\nDernier alinéa canonique."
    assert article.text.count("Premier alinéa canonique.") == 1
    assert "[Article 440]" not in article.text


@pytest.mark.asyncio
async def test_get_article_recovers_batch_boundary_continuation(isolated_test_corpus):
    connection = sqlite3.connect(isolated_test_corpus)
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                50,
                "auscgie",
                "Hypothèques conventionnelles > Article 207",
                "[Article 207]\nLa publication peut être différée pendant un",
            ),
            (
                51,
                "auscgie",
                "AUSCGIE-2014_fr_batch_41-50",
                (
                    "[AUSCGIE-2014_fr_batch_41-50]\n"
                    "Adopté le 30/01/2014 à Ouagadougou (BURKINA FASO)\n"
                    "Publié au Journal Officiel n° spécial du 04/02/2014\n"
                    "délai maximum de quatre-vingt-dix jours.\n"
                    "Article 208\nLe texte du voisin ne doit pas être inclus."
                ),
            ),
        ],
    )
    connection.commit()
    connection.close()

    article = await legal_api.get_article("AUSCGIE", "207")

    assert article.text == ("La publication peut être différée pendant un\ndélai maximum de quatre-vingt-dix jours.")
    assert "Adopté le" not in article.text
    assert "voisin" not in article.text


@pytest.mark.asyncio
async def test_get_article_repairs_missing_and_mislabelled_layout_chunks(isolated_test_corpus):
    connection = sqlite3.connect(isolated_test_corpus)
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (60, "auscgie", "Article 39", "[Article 39]\nTexte de l'article trente-neuf."),
            (
                61,
                "auscgie",
                "Section 2 - Types d'apports",
                (
                    "[Section 2 - Types d'apports]\nChaque associé peut apporter de l'argent, "
                    "des biens ou son industrie à la société."
                ),
            ),
            (62, "auscgie", "Article 41", "[Article 41]\nTexte de l'article quarante et un."),
            (
                63,
                "auscgie",
                "Article 44",
                "[Article 44]\nLes apports réalisés à l'occasion d'une augmentation de",
            ),
            (
                64,
                "auscgie",
                "Article 40",
                "[Article 40]\ncapital peuvent être réalisés par compensation.",
            ),
            (65, "auscgie", "Article 45", "[Article 45]\nTexte de l'article quarante-cinq."),
            (
                70,
                "auscgie",
                "Article 346",
                "[Article 346]\nLa demande comporte la signature des associés à l'origine du projet de",
            ),
            (
                71,
                "auscgie",
                "résolution ;",
                "[résolution ;]\nLorsque le projet concerne un candidat, son identité est indiquée.",
            ),
            (72, "auscgie", "Article 347", "[Article 347]\nDisposition suivante."),
        ],
    )
    connection.commit()
    connection.close()

    article_40 = await legal_api.get_article("AUSCGIE", "40")
    article_44 = await legal_api.get_article("AUSCGIE", "44")
    article_346 = await legal_api.get_article("AUSCGIE", "346")

    assert article_40.text.startswith("Chaque associé peut apporter")
    assert "compensation" not in article_40.text
    assert article_44.text == (
        "Les apports réalisés à l'occasion d'une augmentation de\ncapital peuvent être réalisés par compensation."
    )
    assert "projet de\nrésolution ;\nLorsque le projet" in article_346.text


@pytest.mark.asyncio
async def test_search_ohada_law():
    results = await legal_api.search_ohada_law(query="prescriptions entre commerçants", max_results=3)
    assert isinstance(results, SearchResults)
    assert results.result_count > 0
    assert len(results.results) <= 3
    first_hit = results.results[0]
    assert first_hit.rank == 1
    assert first_hit.act_code is not None
    assert first_hit.snippet
    assert "score" not in first_hit.model_dump()


@pytest.mark.asyncio
async def test_get_provision_at_date():
    result = await legal_api.get_provision_at_date("AUDCG", "16", "2018-03-12")
    assert result.act_code == "AUDCG"
    assert result.status_at_date == "in_force"
    assert result.is_applicable is True
    assert "text" not in result.model_dump()


@pytest.mark.asyncio
async def test_verify_citation():
    # Test valid citation
    res = await legal_api.verify_citation("Article 16 AUDCG")
    assert isinstance(res, CitationVerificationResult)
    assert res.is_valid is True
    assert res.canonical_citation == "Article 16 AUDCG"
    assert res.article_reference == "16"
    assert "matched_article" not in res.model_dump()

    # Test invalid citation
    res_invalid = await legal_api.verify_citation("Article 99999 AUDCG")
    assert res_invalid.is_valid is False


@pytest.mark.asyncio
async def test_verify_citation_with_official_long_title():
    result = await legal_api.verify_citation(
        "Article 326 de l'Acte uniforme relatif au droit des sociétés "
        "commerciales et du groupement d'intérêt économique"
    )
    assert result.is_valid is True
    assert result.act_code == "AUSCGIE"
    assert result.article_reference == "326"


@pytest.mark.asyncio
async def test_get_article_extracts_embedded_article_without_neighbours(isolated_test_corpus):
    connection = sqlite3.connect(isolated_test_corpus)
    connection.execute(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        (
            30,
            "auscgie",
            "Procédures collectives simplifiées",
            (
                "[Procédures collectives simplifiées]\n"
                "Article 227\nTexte du voisin précédent.\n"
                "Article 228\nTexte exact de la disposition recherchée.\n"
                "Article 229\nTexte du voisin suivant."
            ),
        ),
    )
    connection.commit()
    connection.close()

    article = await legal_api.get_article("AUSCGIE", "228")

    assert article.text == "Texte exact de la disposition recherchée."
    assert "voisin précédent" not in article.text
    assert "voisin suivant" not in article.text
    assert article.hierarchy_context.full_path.endswith("Article 228")


@pytest.mark.asyncio
async def test_search_snippet_is_bounded_and_keeps_relevant_context(isolated_test_corpus):
    connection = sqlite3.connect(isolated_test_corpus)
    long_text = "Introduction générale. " + ("contenu ordinaire " * 80) + "motif décisif final."
    connection.execute(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        (31, "auscgie", "Recherche > Article 500", f"[Recherche > Article 500]\n{long_text}"),
    )
    connection.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild')")
    connection.commit()
    connection.close()

    results = await legal_api.search_ohada_law("motif décisif", max_results=1, act_filter="AUSCGIE")

    assert results.result_count == 1
    assert "motif décisif" in results.results[0].snippet
    assert len(results.results[0].snippet) <= 604


@pytest.mark.asyncio
async def test_search_prioritizes_distinct_query_concept_coverage(isolated_test_corpus):
    connection = sqlite3.connect(isolated_test_corpus)
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                40,
                "auscgie",
                "Article 90",
                "[Article 90]\nUne procédure collective étrangère constate la cessation des paiements.",
            ),
            (
                41,
                "auscgie",
                "Article 91",
                (
                    "[Article 91]\nLa procédure collective applicable en cas de cessation des "
                    "paiements impose une déclaration dans un délai déterminé."
                ),
            ),
        ],
    )
    connection.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild')")
    connection.commit()
    connection.close()

    results = await legal_api.search_ohada_law(
        "cessation paiements procédure collective déclaration délai",
        max_results=2,
        act_filter="AUSCGIE",
    )

    assert results.results[0].article_reference == "91"


@pytest.mark.asyncio
async def test_discovery_and_verification_payloads_stay_compact():
    search = await legal_api.search_ohada_law("associé révocation gérant", max_results=5)
    verification = await legal_api.verify_citation("Article 326 AUSCGIE")
    article = await legal_api.get_article("AUSCGIE", "326")

    search_size = len(json.dumps(search.model_dump(mode="json"), ensure_ascii=False))
    verification_size = len(json.dumps(verification.model_dump(mode="json"), ensure_ascii=False))
    article_size = len(json.dumps(article.model_dump(mode="json"), ensure_ascii=False))

    assert search_size <= 7_500
    assert verification_size <= 1_500
    assert verification_size < article_size


@pytest.mark.asyncio
async def test_unknown_act_is_rejected():
    with pytest.raises(ValueError, match="Code d'acte OHADA inconnu"):
        await legal_api.get_act("RELATIF")


@pytest.mark.asyncio
async def test_search_input_limits_are_enforced():
    with pytest.raises(ValueError, match="vide"):
        await legal_api.search_ohada_law("   ")
    with pytest.raises(ValueError, match="max_results"):
        await legal_api.search_ohada_law("société", max_results=10_000)


@pytest.mark.asyncio
async def test_article_and_date_formats_are_validated():
    with pytest.raises(ValueError, match="Référence d'article invalide"):
        await legal_api.get_article("AUDCG", "16; DROP TABLE chunks")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        await legal_api.get_provision_at_date("AUDCG", "16", "12/03/2018")
