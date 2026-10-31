---
title: 11 outils MCP pour le droit OHADA et le SYSCOHADA
description: Référence des 11 outils OHADA MCP Server pour rechercher le droit OHADA, récupérer des articles, vérifier des citations et interroger le SYSCOHADA depuis un assistant IA.
---

# 11 outils MCP pour rechercher et citer le droit OHADA

OHADA MCP Server expose **11 outils en lecture seule** destinés aux assistants IA, agents logiciels et applications LegalTech. Ils couvrent la recherche juridique OHADA, la récupération de textes complets, la vérification de citations et l'interrogation du SYSCOHADA.

## Outils pour le droit OHADA

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

## Outils SYSCOHADA

| Outil | Quand l'utiliser |
|---|---|
| [`search_syscohada`](tools/syscohada.md#search_syscohada) | Découvrir des passages comptables par concepts |
| [`get_syscohada_passages`](tools/syscohada.md#get_syscohada_passages) | Récupérer 1 à 5 passages complets découverts par la recherche |
| [`get_syscohada_account`](tools/syscohada.md#get_syscohada_account) | Obtenir directement tous les passages d'un compte exact |

## Quel outil MCP choisir ?

```text
Référence exacte connue ?
├─ Oui, un article                     → get_article
├─ Oui, plusieurs articles             → get_articles
├─ Oui, un compte SYSCOHADA             → get_syscohada_account
├─ Non, question juridique             → search_ohada_law puis récupération
└─ Non, question comptable             → search_syscohada puis récupération
```

L'objectif est de séparer **découverte** et **récupération** : la recherche identifie les dispositions candidates, puis un outil de récupération fournit le texte complet et les métadonnées qui doivent fonder la réponse de l'assistant.

!!! tip "Éviter les appels inutiles"
    Un `get_article` réussi établit déjà l'existence de la référence et fournit son texte. Il est inutile d'appeler ensuite `verify_citation` pour la même citation.

[Outils juridiques OHADA](tools/legal.md){ .md-button .md-button--primary }
[Outils SYSCOHADA](tools/syscohada.md){ .md-button }
