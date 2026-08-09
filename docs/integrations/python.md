# Intégration Python

L'exemple ci-dessous utilise le SDK Python officiel MCP et le transport Streamable HTTP.

## Installation

```bash
pip install "mcp>=1.29,<2"
```

## Découvrir les outils

```python
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp"


async def main() -> None:
    async with (
        streamable_http_client(MCP_URL) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        for tool in tools.tools:
            print(tool.name, "—", tool.description)


asyncio.run(main())
```

## Appeler un outil

```python
result = await session.call_tool(
    "get_article",
    {
        "act_code": "AUSCGIE",
        "article_reference": "326",
    },
)

if result.isError:
    raise RuntimeError(result.content)

article = result.structuredContent
print(article["text"])
print(article["official_source"]["url"])
```

Les données métier sont fournies dans `structuredContent`. Le champ `content` appartient à l'enveloppe MCP et peut servir aux clients qui n'exploitent pas encore la réponse structurée.

## Recherche puis récupération

```python
search = await session.call_tool(
    "search_ohada_law",
    {
        "query": "révocation judiciaire gérant associé minoritaire",
        "act_filter": "AUSCGIE",
        "max_results": 5,
    },
)

hits = search.structuredContent["results"]
article = await session.call_tool(
    "get_article",
    {
        "act_code": hits[0]["act_code"],
        "article_reference": hits[0]["article_reference"],
    },
)
```

Un extrait de recherche facilite la sélection ; il ne remplace pas le texte complet retourné par `get_article` ou `get_articles`.

## Bonnes pratiques client

- réutiliser une session pendant une opération cohérente ;
- lire `structuredContent` plutôt que parser du texte ;
- borner le nombre d'appels de votre agent tout en autorisant les recherches réellement nécessaires ;
- ne jamais reconstruire une citation à partir du seul intitulé d'un résultat ;
- traiter `isError` avant d'utiliser le résultat ;
- appliquer un timeout et une stratégie de retry uniquement aux erreurs transitoires.
