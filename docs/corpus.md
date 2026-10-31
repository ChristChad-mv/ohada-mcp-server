---
title: Corpus OHADA et SYSCOHADA disponible dans OHADA MCP Server
description: Liste des 13 textes juridiques OHADA et du corpus SYSCOHADA actuellement indexés dans OHADA MCP Server, avec versions, codes et limites de couverture.
---

# Corpus OHADA et SYSCOHADA disponible

OHADA MCP Server indexe actuellement **13 textes juridiques OHADA** ainsi que la publication officielle **SYSCOHADA**. Cette page présente la couverture documentaire utilisée par les outils de recherche et de récupération du serveur MCP.

`list_legal_texts` permet d'obtenir la couverture juridique directement depuis un client MCP.

## 13 textes juridiques OHADA indexés

| Code | Texte | Version indexée |
|---|---|---:|
| `TRAITE` | Traité OHADA révisé | 2008 |
| `AUDCG` | Droit commercial général | 2010 |
| `AUSCGIE` | Sociétés commerciales et GIE | 2014 |
| `AUPCAP` | Procédures collectives d'apurement du passif | 2015 |
| `AUS` | Sûretés | 2010 |
| `AUA` | Arbitrage | 2017 |
| `AUM` | Médiation | 2017 |
| `AUDCIF` | Droit comptable et information financière | 2017 |
| `AUSCOOP` | Sociétés coopératives | 2010 |
| `AUCTMR` | Transport de marchandises par route | 2003 |
| `AUPSRVE` | Recouvrement et voies d'exécution | 2023 |
| `REGLEMENT-ARBITRAGE-CCJA` | Règlement d'arbitrage CCJA | 2017 |
| `REGLEMENT-PROCEDURE-CCJA` | Règlement de procédure CCJA | 2014 |

## SYSCOHADA dans les assistants IA

La publication officielle **Acte uniforme relatif au droit comptable et à l'information financière et système comptable OHADA** est interrogeable avec des outils dédiés. Les réponses conservent les pages, classes, comptes, sous-sections et citations afin qu'un assistant IA puisse produire une réponse traçable.

Les outils [`search_syscohada`](tools/syscohada.md#search_syscohada), [`get_syscohada_passages`](tools/syscohada.md#get_syscohada_passages) et [`get_syscohada_account`](tools/syscohada.md#get_syscohada_account) permettent respectivement de rechercher un concept, récupérer les passages complets et consulter un compte exact.

## Sources et versions

Les objets complets retournent un bloc `official_source` indiquant notamment l'autorité de publication, le Journal officiel, les dates disponibles et l'URL de référence. Les métadonnées de version permettent au client de distinguer le texte indexé d'une interprétation générée par le modèle.

## Ce qui n'est pas encore indexé

- jurisprudence de la CCJA ;
- jurisprudences nationales ;
- doctrine et commentaires privés ;
- guide d'application SYSCOHADA ;
- reconstitution exhaustive de toutes les versions historiques remplacées.

!!! warning "Conséquence pratique"
    Lorsqu'une notion dépend de la jurisprudence — par exemple l'appréciation concrète d'un « juste motif » — le serveur peut établir le texte applicable, mais ne doit pas inventer les critères jurisprudentiels absents du corpus.

[Voir les outils juridiques](tools/legal.md){ .md-button .md-button--primary }
[Voir les outils SYSCOHADA](tools/syscohada.md){ .md-button }
