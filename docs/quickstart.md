---
title: Connecter OHADA MCP Server à Claude, Gemini ou un client MCP
description: Guide de démarrage rapide pour connecter OHADA MCP Server à Claude ou à un client Model Context Protocol et interroger le droit OHADA et le SYSCOHADA en quelques minutes.
---

# Connecter OHADA MCP Server en moins de cinq minutes

Ce guide permet de connecter **OHADA MCP Server** à un assistant IA ou à une application compatible **Model Context Protocol (MCP)**, puis de tester une recherche en droit OHADA ou dans le SYSCOHADA.

## 1. Copier l'endpoint MCP public

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

!!! note "Ce n'est pas une page web"
    L'endpoint `/mcp` utilise le transport **Streamable HTTP**. Si vous l'ouvrez directement dans un navigateur, une erreur indiquant que le client doit accepter `text/event-stream` est normale. Utilisez un client MCP. L'état du service est consultable sur [`/health`](https://ohada-mcp-oa42gsj75q-ew.a.run.app/health).

## 2. Choisir votre client MCP

=== "Claude"

    1. Ouvrez **Settings → Connectors**.
    2. Choisissez **Add custom connector**.
    3. Nommez le connecteur `OHADA MCP`.
    4. Collez l'endpoint ci-dessus.
    5. Activez le connecteur dans **Search and tools**.

    [Instructions détaillées pour Claude](integrations/claude.md)

=== "Application Python"

    Installez le SDK officiel MCP puis ouvrez une session Streamable HTTP :

    ```bash
    pip install "mcp>=1.29,<2"
    ```

    [Exemple Python complet](integrations/python.md)

=== "Autre client MCP"

    Lorsque le client demande une URL de serveur distant, utilisez :

    ```json
    {
      "mcpServers": {
        "ohada": {
          "url": "https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp"
        }
      }
    }
    ```

    Le nom exact des champs dépend du client. Le transport requis est **Streamable HTTP**.

## 3. Poser une question en droit OHADA

Essayez :

> Un associé minoritaire d'une SARL peut-il demander la révocation judiciaire du gérant ? Cite précisément le fondement utilisé.

Le parcours attendu est généralement :

```text
search_ohada_law → get_article → réponse fondée sur l'article complet
```

Si la question indique déjà `Article 326 AUSCGIE`, le client peut appeler directement `get_article` sans recherche préalable.

## 4. Tester le SYSCOHADA

Essayez :

> Selon le SYSCOHADA, comment fonctionne le compte 101 — Capital social ?

Comme le compte exact est connu, le parcours recommandé est :

```text
get_syscohada_account → réponse fondée sur les passages complets et leurs pages
```

## 5. Vérifier la qualité de la réponse

Une réponse bien fondée doit comporter :

- la réponse directe à la question ;
- le code exact du texte, par exemple `AUSCGIE` ;
- la référence de l'article ou la page SYSCOHADA ;
- la version et la source lorsqu'elles sont retournées ;
- une distinction entre le contenu du texte et ce qui nécessiterait jurisprudence ou interprétation.

[Comprendre les enchaînements d'outils](workflows.md){ .md-button .md-button--primary }
[Voir les 11 outils MCP](tools.md){ .md-button }
