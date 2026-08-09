# Démarrage rapide

Cette page permet de vérifier OHADA MCP en moins de cinq minutes.

## 1. Copier l'endpoint

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

!!! note "Ce n'est pas une page web"
    L'endpoint `/mcp` utilise le transport **Streamable HTTP**. Si vous l'ouvrez directement dans un navigateur, une erreur indiquant que le client doit accepter `text/event-stream` est normale. Utilisez un client MCP. L'état du service est consultable sur [`/health`](https://ohada-mcp-oa42gsj75q-ew.a.run.app/health).

## 2. Choisir votre parcours

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

## 3. Poser une question juridique

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

## 5. Vérifier le résultat

Une réponse bien fondée doit comporter :

- la réponse directe à la question ;
- le code exact du texte, par exemple `AUSCGIE` ;
- la référence de l'article ou la page SYSCOHADA ;
- une distinction entre le contenu du texte et ce qui nécessiterait jurisprudence ou interprétation.

[Comprendre les enchaînements d'outils](workflows.md){ .md-button .md-button--primary }
[Résoudre une erreur](limits.md){ .md-button }
