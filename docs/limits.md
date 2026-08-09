# Limites et erreurs

Les limites protègent la disponibilité du service et empêchent qu'un agent envoie des recherches démesurées.

## Limites publiques

| Élément | Limite |
|---|---:|
| Corps d'une requête HTTP | 65 536 octets |
| Requête de recherche | 1 000 caractères |
| Termes par recherche | 32 |
| Résultats de recherche | 1 à 10 |
| Articles dans `get_articles` | 2 à 5 |
| Passages dans `get_syscohada_passages` | 1 à 5 |
| Citation à vérifier | 500 caractères |
| Débit public | 120 requêtes par minute et par client, par instance |

## Codes HTTP fréquents

| Code | Signification | Action client |
|---:|---|---|
| `400` | Requête ou enveloppe MCP invalide | Corriger les paramètres ; ne pas retry automatiquement |
| `403` | `Host` ou `Origin` non autorisé | Utiliser l'endpoint officiel depuis un client conforme |
| `413` | Corps trop volumineux | Réduire la requête |
| `429` | Limite de débit atteinte | Respecter `Retry-After`, puis réessayer |
| `500` / `503` | Erreur transitoire ou corpus indisponible | Retry borné avec délai progressif |

## Erreurs d'outil

Un appel MCP peut réussir au niveau HTTP tout en retournant `isError: true` pour une erreur métier : code d'acte inconnu, article introuvable, date invalide ou paramètre hors limite.

Ne transformez pas automatiquement une référence introuvable en une autre référence. Recherchez le concept juridique et expliquez l'ambiguïté au lecteur.

## `Not Acceptable: Client must accept text/event-stream`

Cette erreur apparaît généralement lorsque `/mcp` est ouvert comme une page web ou appelé avec de mauvais en-têtes. Elle ne signale pas une panne. Utilisez un SDK MCP ou vérifiez [`/health`](https://ohada-mcp-oa42gsj75q-ew.a.run.app/health).

## Stratégie de retry

- aucun retry pour une validation `400` ;
- attendre la valeur `Retry-After` pour un `429` ;
- pour une erreur `5xx`, effectuer quelques retries avec délai exponentiel et jitter ;
- ne jamais rejouer indéfiniment un appel identique.
