# Protocole et endpoint

## Transport

OHADA MCP utilise **MCP Streamable HTTP** sur HTTPS.

| Élément | Valeur |
|---|---|
| Endpoint | `https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp` |
| Transport | Streamable HTTP |
| Réponses | JSON / flux événementiel selon la négociation MCP |
| Mode | Stateless |
| Authentification | Aucune pour le niveau public actuel |
| Outils | Lecture seule et idempotents |

## Pourquoi le navigateur affiche une erreur

Une navigation web ordinaire envoie un en-tête `Accept` destiné à recevoir une page HTML. L'endpoint MCP attend la négociation du protocole, notamment `application/json` et `text/event-stream`. Une erreur `Not Acceptable` dans le navigateur ne signifie donc pas que le serveur est indisponible.

Pour vérifier simplement le service :

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/health
```

## Cycle d'une session

Un client conforme effectue généralement :

```text
connexion → initialize → tools/list → tools/call → fermeture
```

N'envoyez pas directement des requêtes REST inventées vers `/mcp`. Utilisez un SDK ou un client compatible MCP, qui gère les en-têtes et l'enveloppe JSON-RPC.

## Endpoint de santé

`GET /health` confirme uniquement la disponibilité technique et la présence des corpus. Il ne retourne ni contenu juridique ni information utilisateur.
