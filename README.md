# OHADA MCP Server — Droit OHADA & SYSCOHADA pour assistants IA

> Serveur **Model Context Protocol (MCP)** public et open source pour rechercher, récupérer et citer le droit OHADA et le SYSCOHADA depuis Claude, Gemini, des agents IA et des applications LegalTech.

**Documentation :** https://christchad-mv.github.io/ohada-mcp-server/  
**Endpoint MCP :** `https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp`  
**Transport :** Streamable HTTP  
**Auteur :** Christ Chadrak Mvoungou  
**Statut :** initiative indépendante, sans affiliation officielle avec l'OHADA

## Pourquoi OHADA MCP Server ?

Les modèles de langage peuvent produire des réponses juridiques sans source fiable lorsqu'ils travaillent uniquement à partir de leur mémoire. OHADA MCP Server fournit au contraire des **outils de recherche et de récupération documentaire** permettant à un assistant IA de retrouver une disposition OHADA, récupérer son texte complet, sa version et ses métadonnées de source avant de générer une réponse.

Le serveur couvre notamment :

- recherche dans **13 textes juridiques OHADA** ;
- récupération du texte intégral d'un article exact ;
- récupération groupée de plusieurs articles ;
- vérification et normalisation de citations ;
- contrôle de la version indexée à une date ;
- recherche dans le **SYSCOHADA** ;
- récupération de passages et comptes SYSCOHADA avec leur contexte.

## Connexion rapide

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

Le chemin `/mcp` est un endpoint de protocole, pas une page web. Un navigateur ordinaire peut donc recevoir une erreur indiquant que le client doit accepter `text/event-stream`. Utilisez un client compatible MCP.

### Claude

Avec une version de Claude prenant en charge les connecteurs MCP personnalisés :

1. Ouvrez **Settings → Connectors**.
2. Cliquez sur **Add custom connector**.
3. Nommez-le `OHADA MCP` et collez l'URL ci-dessus.
4. Activez les outils dans la conversation.

Guide détaillé : https://christchad-mv.github.io/ohada-mcp-server/integrations/claude/

### Autres clients MCP

```json
{
  "mcpServers": {
    "ohada": {
      "url": "https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp"
    }
  }
}
```

## Les 11 outils disponibles

### Droit OHADA

- `list_legal_texts` — liste les textes et codes canoniques disponibles.
- `search_ohada_law` — découvre les dispositions pertinentes à partir d'une question ou de concepts.
- `get_article` — récupère le texte complet, la hiérarchie, la version et la source d'un article exact.
- `get_articles` — récupère 2 à 5 articles exacts en un seul appel.
- `get_act` — retourne les métadonnées générales d'un Acte uniforme.
- `get_version` — retourne la version actuellement indexée d'un texte.
- `get_provision_at_date` — contrôle l'applicabilité de la version indexée à une date.
- `verify_citation` — vérifie et normalise une citation.

### SYSCOHADA

- `search_syscohada` — découvre des passages comptables par concepts, compte ou classe.
- `get_syscohada_passages` — récupère 1 à 5 passages complets.
- `get_syscohada_account` — récupère les passages indexés d'un compte exact.

## Parcours recommandé

1. Si la référence exacte est connue, appelez directement `get_article`, `get_articles` ou `get_syscohada_account`.
2. Sinon, recherchez avec `search_ohada_law` ou `search_syscohada`.
3. Récupérez le contenu complet des résultats retenus avant de rédiger la réponse.
4. Citez le code du texte, la référence, la version et la source retournée.
5. Ne jamais inventer une disposition ou une jurisprudence absente du corpus.

## Couverture et limites

Le corpus couvre actuellement **13 textes juridiques OHADA** ainsi que la publication officielle SYSCOHADA. La jurisprudence CCJA et nationale, la doctrine privée et le guide d'application SYSCOHADA ne sont pas encore indexés.

Documentation du corpus : https://christchad-mv.github.io/ohada-mcp-server/corpus/

## Documentation

- [Vue d'ensemble](https://christchad-mv.github.io/ohada-mcp-server/)
- [Démarrage rapide](https://christchad-mv.github.io/ohada-mcp-server/quickstart/)
- [Connexion à Claude](https://christchad-mv.github.io/ohada-mcp-server/integrations/claude/)
- [Référence des outils](https://christchad-mv.github.io/ohada-mcp-server/tools/)
- [Corpus OHADA et SYSCOHADA](https://christchad-mv.github.io/ohada-mcp-server/corpus/)
- [Questions fréquentes](https://christchad-mv.github.io/ohada-mcp-server/faq/)
- [Confidentialité](https://christchad-mv.github.io/ohada-mcp-server/privacy/)
- [Sécurité](https://christchad-mv.github.io/ohada-mcp-server/security/)
- [llms.txt](https://christchad-mv.github.io/ohada-mcp-server/llms.txt)

## Licence et avertissement

Le code est distribué sous [licence MIT](LICENSE). OHADA MCP Server est un outil de recherche documentaire et **ne constitue pas un conseil juridique**.
