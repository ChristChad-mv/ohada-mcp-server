# OHADA MCP

Le serveur MCP public de recherche juridique OHADA.

OHADA MCP permet à Claude, Gemini et aux clients compatibles MCP de rechercher les textes OHADA, de récupérer un article complet et de vérifier une citation.

> Projet indépendant créé par Christ Chad. Il n'est pas encore affilié, approuvé ou exploité officiellement par l'OHADA.

## Connexion

URL du serveur :

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

### Claude

Avec Claude Pro, Max, Team ou Enterprise :

1. Ouvrez **Settings → Connectors** dans Claude ou Claude Desktop.
2. Cliquez sur **Add custom connector**.
3. Nommez-le `OHADA MCP` et collez l'URL ci-dessus.
4. Activez les outils dans le menu **Search and tools** d'une conversation.

[Guide officiel des connecteurs personnalisés Claude](https://support.anthropic.com/en/articles/11175166-about-custom-integrations-using-remote-mcp)

### Autres clients MCP

Utilisez cette configuration lorsque votre client demande une URL de serveur MCP :

```json
{
  "mcpServers": {
    "ohada": {
      "url": "https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp"
    }
  }
}
```

## Ce que le serveur fournit

- recherche de dispositions pertinentes ;
- texte intégral d'un article et de son contexte hiérarchique ;
- récupération groupée de plusieurs articles ;
- contrôle d'une citation et de la version indexée.

Le corpus couvre actuellement 13 textes OHADA. La jurisprudence CCJA et nationale n'est pas encore incluse.

## Confidentialité

OHADA MCP ne conserve ni le texte des questions ni les recherches des utilisateurs. N'envoyez pas de dossier client, données personnelles ou informations confidentielles à ce serveur public. Claude, Gemini ou tout autre assistant connecté applique sa propre politique de confidentialité.

## Documentation

- [Connexion rapide](docs/quickstart.md)
- [Référence des outils](docs/tools.md)
- [Confidentialité](docs/privacy.md)

## Licence

Le code est distribué sous [licence MIT](LICENSE). OHADA MCP est un outil de recherche documentaire, pas un conseil juridique.
