from ohada_mcp.citation_guard import (
    remove_unsupported_blocks,
    retrieved_citations,
    unsupported_citations,
)


def tool_calls():
    return [
        {
            "tool": "get_articles",
            "output": {"articles": [{"act_code": "AUSCGIE", "article_reference": "440", "text": "Texte complet"}]},
        },
        {
            "tool": "get_article",
            "output": {"error": "Article 440-1 introuvable"},
        },
    ]


def test_only_successful_full_text_retrievals_are_allowed():
    assert retrieved_citations(tool_calls()) == {("AUSCGIE", "440")}


def test_guard_rejects_an_unretrieved_affirmative_citation():
    answer = "L'Article 440 AUSCGIE fixe la procédure.\nL'Article 443, alinéa 2 AUSCGIE ajoute une sanction."

    assert unsupported_citations(answer, tool_calls()) == ["Article 443 AUSCGIE"]


def test_negative_missing_reference_statement_is_permitted():
    answer = "L'Article 440-1 AUSCGIE n'existe pas dans le corpus chargé."

    assert unsupported_citations(answer, tool_calls()) == []


def test_fail_closed_removes_the_unsupported_block():
    answer = "Règle valide (Article 440 AUSCGIE).\n\nRègle inventée (Article 443 AUSCGIE)."

    cleaned = remove_unsupported_blocks(answer, ["Article 443 AUSCGIE"])

    assert "Article 440" in cleaned
    assert "Article 443" not in cleaned
    assert "a été retirée" in cleaned
