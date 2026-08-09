# Choisir un outil

OHADA MCP expose **11 outils en lecture seule**. Cette page sert de carte d'orientation ; les pages suivantes documentent chaque paramètre et chaque format de réponse.

## Droit OHADA

| Outil | Quand l'utiliser |
|---|---|
| [`search_ohada_law`](tools/legal.md#search_ohada_law) | Découvrir des dispositions lorsqu'aucune référence exacte n'est connue |
| [`get_article`](tools/legal.md#get_article) | Récupérer un article exact avec texte, hiérarchie, version et source |
| [`get_articles`](tools/legal.md#get_articles) | Récupérer 2 à 5 articles exacts en un appel |
| [`get_act`](tools/legal.md#get_act) | Lire les métadonnées générales d'un texte |
| [`list_legal_texts`](tools/legal.md#list_legal_texts) | Connaître les textes couverts et leurs codes |
| [`get_version`](tools/legal.md#get_version) | Identifier la version actuellement indexée |
| [`get_provision_at_date`](tools/legal.md#get_provision_at_date) | Contrôler l'applicabilité de cette version à une date |
| [`verify_citation`](tools/legal.md#verify_citation) | Vérifier formellement une citation fournie |

## SYSCOHADA

| Outil | Quand l'utiliser |
|---|---|
| [`search_syscohada`](tools/syscohada.md#search_syscohada) | Découvrir des passages comptables par concepts |
| [`get_syscohada_passages`](tools/syscohada.md#get_syscohada_passages) | Récupérer 1 à 5 passages complets découverts par la recherche |
| [`get_syscohada_account`](tools/syscohada.md#get_syscohada_account) | Obtenir directement tous les passages d'un compte exact |

## Règle de sélection

```text
Référence exacte connue ?
├─ Oui, un article                    → get_article
├─ Oui, plusieurs articles            → get_articles
├─ Oui, un compte SYSCOHADA            → get_syscohada_account
├─ Non, question juridique             → search_ohada_law puis récupération
└─ Non, question comptable             → search_syscohada puis récupération
```

!!! tip "Éviter les appels inutiles"
    Un `get_article` réussi établit déjà l'existence de la référence et fournit son texte. Il est inutile d'appeler ensuite `verify_citation` pour la même citation.

[Outils juridiques](tools/legal.md){ .md-button .md-button--primary }
[Outils SYSCOHADA](tools/syscohada.md){ .md-button }
