---
title: OHADA MCP Server — Droit OHADA et SYSCOHADA pour assistants IA
description: OHADA MCP Server est un serveur Model Context Protocol public pour rechercher, récupérer et citer les textes OHADA et le SYSCOHADA depuis Claude, Gemini et des agents IA ou applications LegalTech.
---

# OHADA MCP Server : le droit OHADA et le SYSCOHADA dans les assistants IA

**OHADA MCP Server** est une infrastructure juridique ouverte qui permet à Claude, Gemini et aux autres clients compatibles **Model Context Protocol (MCP)** d'interroger le droit OHADA avec des sources structurées.

Le serveur permet de **rechercher les textes OHADA**, **récupérer le texte intégral d'un article**, **vérifier une citation**, **contrôler la version applicable** et **consulter le SYSCOHADA**. Il peut être utilisé directement dans un assistant IA ou intégré à une application LegalTech.

<div class="endpoint-card" markdown>

**Endpoint MCP public**

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

[Se connecter en 5 minutes](quickstart.md){ .md-button .md-button--primary }
[Voir les 11 outils](tools.md){ .md-button }

</div>

!!! info "Initiative indépendante"
    OHADA MCP Server est créé par **Christ Chadrak Mvoungou**. Le projet n'est pas encore affilié, approuvé ou exploité officiellement par l'OHADA.

## À quoi sert OHADA MCP Server ?

OHADA MCP Server fournit une couche d'accès structurée au droit des affaires OHADA pour les assistants IA, agents logiciels et applications juridiques. Il évite de demander au modèle de langage de « connaître » le droit par mémoire : le client MCP peut rechercher les dispositions pertinentes puis récupérer le texte complet et sa source avant de rédiger sa réponse.

Cas d'usage principaux :

- assistant juridique IA fondé sur les textes OHADA ;
- recherche d'articles dans les Actes uniformes ;
- vérification et normalisation de citations juridiques OHADA ;
- interrogation du SYSCOHADA et des comptes comptables ;
- intégration d'une API juridique OHADA dans une LegalTech ;
- agents IA nécessitant des réponses traçables et sourcées.

## Que voulez-vous faire ?

<div class="grid cards" markdown>

-   :material-robot-outline:{ .lg .middle } **Connecter un assistant IA**

    ---

    Ajoutez l'URL distante dans Claude ou dans un autre client MCP, puis posez directement vos questions sur le droit OHADA.

    [:octicons-arrow-right-24: Démarrage rapide](quickstart.md)

-   :material-code-braces:{ .lg .middle } **Construire une LegalTech**

    ---

    Utilisez le SDK MCP pour découvrir les outils et exploiter leurs réponses structurées dans votre propre application.

    [:octicons-arrow-right-24: Intégration Python](integrations/python.md)

-   :material-scale-balance:{ .lg .middle } **Interroger le droit OHADA**

    ---

    Recherchez une règle, récupérez le texte intégral de l'article et conservez sa version et sa source officielle.

    [:octicons-arrow-right-24: Outils juridiques](tools/legal.md)

-   :material-calculator-variant-outline:{ .lg .middle } **Consulter le SYSCOHADA**

    ---

    Recherchez un concept comptable ou récupérez directement le contexte complet d'un compte SYSCOHADA.

    [:octicons-arrow-right-24: Outils SYSCOHADA](tools/syscohada.md)

</div>

## Comprendre les outils en une minute

| Votre besoin | Outil à utiliser |
|---|---|
| Rechercher une règle sans connaître l'article | `search_ohada_law` |
| Lire un article exact et complet | `get_article` |
| Lire 2 à 5 articles en un seul appel | `get_articles` |
| Vérifier uniquement une citation fournie | `verify_citation` |
| Contrôler l'applicabilité à une date | `get_provision_at_date` |
| Rechercher une règle comptable | `search_syscohada` |
| Lire les passages comptables retenus | `get_syscohada_passages` |
| Consulter directement un compte exact | `get_syscohada_account` |

Le principe essentiel est simple : **les outils de recherche découvrent des candidats ; les outils de récupération fournissent le texte complet qui fonde la réponse finale**.

## Quels textes OHADA sont disponibles ?

Le corpus couvre actuellement **13 textes juridiques OHADA**, notamment le Traité révisé, l'AUDCG, l'AUSCGIE, l'AUPCAP, l'Acte uniforme sur les sûretés, l'arbitrage, la médiation, le droit comptable, les sociétés coopératives, le transport routier, les procédures simplifiées de recouvrement et les règlements CCJA.

Le **SYSCOHADA** est également interrogeable avec ses pages, classes, comptes, sous-sections et citations. Consultez la page [Textes OHADA et corpus SYSCOHADA](corpus.md) pour la couverture détaillée.

## Est-ce une API OHADA officielle ?

Non. OHADA MCP Server est une **initiative indépendante et open source**. Il n'est pas un service officiel de l'Organisation pour l'harmonisation en Afrique du droit des affaires. Les réponses exposent les sources documentaires disponibles afin que l'utilisateur puisse vérifier le texte et sa version.

## Garanties du service

OHADA MCP Server est en lecture seule. Il n'exécute pas de commandes, ne modifie pas les textes et n'accepte pas d'URL arbitraire. L'application ne conserve pas le texte des questions ou des recherches. Consultez les pages [Confidentialité](privacy.md) et [Sécurité](security.md).

!!! warning "Information juridique, pas conseil juridique"
    Les réponses d'un assistant restent des synthèses automatisées. Vérifiez la version applicable, la publication officielle et, lorsque nécessaire, la jurisprudence ou l'avis d'un professionnel qualifié.

## Documentation pour humains et agents IA

La documentation est structurée pour être facilement parcourue par les développeurs, moteurs de recherche et assistants IA. Une synthèse machine-readable est disponible dans [`llms.txt`](llms.txt), tandis que le [démarrage rapide](quickstart.md), la [référence des outils](tools.md), le [corpus](corpus.md) et la [FAQ](faq.md) donnent les informations détaillées.
