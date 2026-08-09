# Connecter Claude

OHADA MCP peut être ajouté comme connecteur MCP distant personnalisé.

## Configuration

1. Dans Claude ou Claude Desktop, ouvrez **Settings → Connectors**.
2. Cliquez sur **Add custom connector**.
3. Utilisez le nom `OHADA MCP`.
4. Collez l'URL :

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

5. Ouvrez une conversation puis activez OHADA MCP dans **Search and tools**.

[Consulter le guide officiel Anthropic](https://support.anthropic.com/en/articles/11175166-about-custom-integrations-using-remote-mcp)

## Vérifier la connexion

Demandez d'abord :

> Quels textes juridiques sont actuellement disponibles dans OHADA MCP ?

Claude devrait utiliser `list_legal_texts`.

Essayez ensuite :

> Récupère l'article 16 de l'AUDCG et explique uniquement ce que son texte permet d'établir.

Claude devrait utiliser directement `get_article` avec :

```json
{
  "act_code": "AUDCG",
  "article_reference": "16"
}
```

## Si Claude multiplie les appels

Les descriptions des outils lui indiquent déjà le parcours recommandé. Vous pouvez renforcer la consigne dans votre message :

> Recherche d'abord les références utiles, récupère ensuite en un seul appel tous les articles nécessaires, puis réponds uniquement à partir de leurs textes complets.

La qualité des sources reste prioritaire : un appel supplémentaire est justifié s'il manque une disposition indispensable.

## Authentification

Le serveur public ne demande actuellement ni compte ni clé API. Il expose uniquement des données publiques au travers d'outils en lecture seule.

!!! warning "Données confidentielles"
    Ne transmettez pas de dossier client ou de secret professionnel. Claude applique sa propre politique de traitement des conversations, distincte de celle d'OHADA MCP.
