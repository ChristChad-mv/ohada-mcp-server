# Sécurité

OHADA MCP expose des textes publics au travers d'outils strictement en lecture seule.

## Protections actives

- HTTPS et transport MCP Streamable HTTP ;
- validation exacte des domaines et origines autorisés ;
- protection contre le DNS rebinding ;
- limites de taille, de résultats et de débit ;
- bases ouvertes en lecture seule et en mode immuable ;
- conteneur exécuté sans privilèges ;
- dépendances verrouillées et vérifiées par empreinte ;
- aucun appel vers une URL fournie par l'utilisateur ;
- aucune exécution de commande ou modification du corpus ;
- monitoring de disponibilité et des erreurs serveur.

## Accès public

Le niveau actuel ne demande ni compte ni clé API. Cette décision correspond à la nature publique des données et au caractère en lecture seule des outils.

Si des ressources privées, des quotas individuels ou des outils d'écriture sont ajoutés, l'authentification devra suivre le standard OAuth prévu par MCP avec validation de l'audience des jetons.

## Signaler une vulnérabilité

N'ouvrez pas d'issue publique pour une vulnérabilité exploitable. Utilisez **Security → Report a vulnerability** dans le [dépôt GitHub](https://github.com/ChristChad-mv/ohada-mcp-server) et indiquez la version concernée, les étapes de reproduction et l'impact observé.

La politique complète est disponible dans [`SECURITY.md`](https://github.com/ChristChad-mv/ohada-mcp-server/blob/master/SECURITY.md).
