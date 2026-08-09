from ohada_mcp.demo_orchestration import (
    authoritative_source_packet,
    correction_contents,
    final_synthesis_contents,
)


def _calls():
    return [
        {"tool": "search_syscohada", "output": {"results": [{"snippet": "court"}]}},
        {
            "tool": "get_syscohada_passages",
            "output": {"passages": [{"text": "texte complet", "page_start": 105}]},
        },
    ]


def test_final_synthesis_uses_only_full_sources_and_plain_text_protocol():
    packet = authoritative_source_packet(_calls())
    contents = final_synthesis_contents(
        [{"role": "user", "content": "Quel est l'objectif du tableau ?"}],
        _calls(),
    )

    assert "search_syscohada" not in packet
    assert "get_syscohada_passages" in packet
    assert contents[0]["role"] == "user"
    assert set(contents[0]["parts"][0]) == {"text"}
    assert "functionCall" not in str(contents)
    assert "functionResponse" not in str(contents)


def test_correction_request_is_also_protocol_independent():
    contents = correction_contents(
        [{"role": "user", "content": "Question"}],
        _calls(),
        "Selon l'Article 999 AUSCGIE",
        ["Article 999 AUSCGIE"],
    )

    text = contents[0]["parts"][0]["text"]
    assert "Article 999 AUSCGIE" in text
    assert "texte complet" in text
    assert "functionCall" not in str(contents)
