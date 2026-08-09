"""Pure helpers used by the private demonstration client's final synthesis."""

from __future__ import annotations

import json

AUTHORITATIVE_FULL_TEXT_TOOLS = {
    "get_article",
    "get_articles",
    "get_syscohada_passages",
    "get_syscohada_account",
}


def latest_user_question(messages_history: list[dict]) -> str:
    return next(
        (str(message.get("content", "")) for message in reversed(messages_history) if message.get("role") == "user"),
        "",
    )


def authoritative_source_packet(tool_calls: list[dict]) -> str:
    """Keep full retrieval outputs and discard discovery-only snippets."""
    sources = [
        {"tool": call["tool"], "output": call["output"]}
        for call in tool_calls
        if call["tool"] in AUTHORITATIVE_FULL_TEXT_TOOLS
    ]
    return json.dumps(sources, ensure_ascii=False, separators=(",", ":"))


def final_synthesis_contents(messages_history: list[dict], tool_calls: list[dict]) -> list[dict]:
    """Build a clean request with no stale function-call protocol history."""
    return [
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"QUESTION INITIALE\n{latest_user_question(messages_history)}\n\n"
                        "SOURCES INTÉGRALES RÉCUPÉRÉES\n"
                        f"{authoritative_source_packet(tool_calls)}\n\n"
                        "Les recherches sont terminées. Répondez maintenant sans appeler "
                        "d'outil, exclusivement à partir de ces sources intégrales. Si elles "
                        "ne permettent pas d'établir un élément demandé, indiquez précisément "
                        "cette limite."
                    )
                }
            ],
        }
    ]


def correction_contents(
    messages_history: list[dict],
    tool_calls: list[dict],
    draft_answer: str,
    unknown_citations: list[str],
) -> list[dict]:
    """Build a citation-correction request independent of tool-call history."""
    return [
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"QUESTION INITIALE\n{latest_user_question(messages_history)}\n\n"
                        "SOURCES INTÉGRALES RÉCUPÉRÉES\n"
                        f"{authoritative_source_packet(tool_calls)}\n\n"
                        f"RÉPONSE À CORRIGER\n{draft_answer}\n\n"
                        "Réécris intégralement la réponse sans appeler d'outil. Supprime toute "
                        "règle reposant sur ces citations dont le texte intégral n'a pas été "
                        f"récupéré : {', '.join(unknown_citations)}. Conserve uniquement les "
                        "règles soutenues par les résultats get_article/get_articles ou les "
                        "passages SYSCOHADA complets déjà présents."
                    )
                }
            ],
        }
    ]
