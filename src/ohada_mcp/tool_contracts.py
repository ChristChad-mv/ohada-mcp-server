"""Single source of truth for MCP and Gemini tool-selection contracts."""

TOOL_DESCRIPTIONS = {
    "search_ohada_law": (
        "Découvre des dispositions candidates par recherche textuelle dans le corpus OHADA. "
        "Retourne uniquement des extraits courts et des références. Utiliser ensuite get_article "
        "pour lire intégralement chaque disposition retenue. Ne pas multiplier les recherches si "
        "les premières références répondent déjà à la question."
    ),
    "get_article": (
        "Retourne le texte normatif intégral et reconstruit d'un article OHADA exact, avec sa "
        "hiérarchie, sa version et sa source officielle. À utiliser lorsqu'une seule disposition "
        "est matériellement nécessaire ; utiliser get_articles pour deux à cinq dispositions."
    ),
    "get_articles": (
        "Retourne en un seul appel le texte normatif intégral de deux à cinq articles exacts. "
        "À préférer après une recherche lorsque plusieurs dispositions sont matériellement "
        "nécessaires. Utiliser get_article pour une seule référence. Les erreurs sont isolées "
        "par référence afin de préserver les articles valides."
    ),
    "get_act": (
        "Retourne les métadonnées complètes d'un texte OHADA identifié par son code. À utiliser "
        "pour une question portant sur l'acte lui-même, pas pour lire un article."
    ),
    "list_legal_texts": (
        "Retourne le catalogue compact des textes actuellement indexés. À utiliser uniquement "
        "pour connaître la couverture ou identifier un code d'acte."
    ),
    "get_version": (
        "Retourne les métadonnées de la version actuellement indexée d'un texte. L'historique "
        "exhaustif des versions antérieures n'est pas encore disponible."
    ),
    "get_provision_at_date": (
        "Contrôle si la version indexée d'un article était applicable à une date ISO. Retourne "
        "des métadonnées temporelles compactes, sans répéter le texte ; appeler get_article si "
        "le contenu intégral est nécessaire. Ne reconstitue pas un ancien libellé remplacé."
    ),
    "verify_citation": (
        "Vérifie et normalise une citation fournie par l'utilisateur. Retourne seulement la "
        "référence canonique et son statut, jamais le texte de l'article. Ne pas appeler cet "
        "outil après un get_article ou get_articles réussi pour la même référence."
    ),
}


GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "search_ohada_law",
        "description": TOOL_DESCRIPTIONS["search_ohada_law"],
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "Question ou concepts juridiques ciblés en français.",
                },
                "max_results": {
                    "type": "INTEGER",
                    "description": "Nombre de résultats distincts, de 1 à 10 (défaut : 5).",
                },
                "act_filter": {
                    "type": "STRING",
                    "description": "Code canonique facultatif, par exemple AUPCAP ou AUSCGIE.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_article",
        "description": TOOL_DESCRIPTIONS["get_article"],
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "act_code": {
                    "type": "STRING",
                    "description": "Code canonique de l'acte, par exemple AUDCG, AUSCGIE ou AUPCAP.",
                },
                "article_reference": {
                    "type": "STRING",
                    "description": "Référence exacte, par exemple 16, 655-1 ou 27 ter.",
                },
            },
            "required": ["act_code", "article_reference"],
        },
    },
    {
        "name": "get_articles",
        "description": TOOL_DESCRIPTIONS["get_articles"],
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "articles": {
                    "type": "ARRAY",
                    "description": "Deux à cinq références exactes et distinctes.",
                    "minItems": 2,
                    "maxItems": 5,
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "act_code": {
                                "type": "STRING",
                                "description": "Code canonique de l'acte.",
                            },
                            "article_reference": {
                                "type": "STRING",
                                "description": "Référence exacte de l'article.",
                            },
                        },
                        "required": ["act_code", "article_reference"],
                    },
                }
            },
            "required": ["articles"],
        },
    },
    {
        "name": "get_act",
        "description": TOOL_DESCRIPTIONS["get_act"],
        "parameters": {
            "type": "OBJECT",
            "properties": {"act_code": {"type": "STRING", "description": "Code canonique du texte OHADA."}},
            "required": ["act_code"],
        },
    },
    {
        "name": "list_legal_texts",
        "description": TOOL_DESCRIPTIONS["list_legal_texts"],
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_version",
        "description": TOOL_DESCRIPTIONS["get_version"],
        "parameters": {
            "type": "OBJECT",
            "properties": {"act_code": {"type": "STRING", "description": "Code canonique du texte OHADA."}},
            "required": ["act_code"],
        },
    },
    {
        "name": "get_provision_at_date",
        "description": TOOL_DESCRIPTIONS["get_provision_at_date"],
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "act_code": {"type": "STRING", "description": "Code canonique du texte OHADA."},
                "article_reference": {"type": "STRING", "description": "Référence exacte de l'article."},
                "target_date": {"type": "STRING", "description": "Date au format YYYY-MM-DD."},
            },
            "required": ["act_code", "article_reference", "target_date"],
        },
    },
    {
        "name": "verify_citation",
        "description": TOOL_DESCRIPTIONS["verify_citation"],
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "citation_text": {
                    "type": "STRING",
                    "description": "Citation à contrôler, par exemple Article 16 AUDCG.",
                }
            },
            "required": ["citation_text"],
        },
    },
]
