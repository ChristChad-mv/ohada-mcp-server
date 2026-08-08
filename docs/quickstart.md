# Démarrage rapide

## URL du serveur

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

## Claude

Les connecteurs MCP distants personnalisés sont disponibles avec Claude Pro, Max, Team et Enterprise.

1. Dans Claude ou Claude Desktop, ouvrez **Settings → Connectors**.
2. Cliquez sur **Add custom connector**.
3. Saisissez `OHADA MCP`, puis l'URL ci-dessus.
4. Dans une conversation, activez ses outils via **Search and tools**.

[Guide officiel des connecteurs personnalisés Claude](https://support.anthropic.com/en/articles/11175166-about-custom-integrations-using-remote-mcp)

## Autres clients

Ajoutez cette URL comme serveur MCP distant dans votre client. Exemple générique :

```json
{
  "mcpServers": {
    "ohada": {
      "url": "https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp"
    }
  }
}
```

## Vérification

Demandez ensuite :

> Quel est le délai de prescription entre commerçants selon l'AUDCG ? Cite précisément l'article utilisé.

Le client devrait appeler `search_ohada_law`, puis `get_article` pour une disposition retenue ou `get_articles` pour deux à cinq dispositions. `verify_citation` est réservé au contrôle formel d'une citation fournie, sans besoin de relire son contenu.
