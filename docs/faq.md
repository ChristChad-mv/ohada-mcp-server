---
title: FAQ — OHADA MCP Server, droit OHADA, SYSCOHADA et assistants IA
description: Réponses aux questions fréquentes sur OHADA MCP Server : fonctionnement du serveur MCP, droit OHADA, SYSCOHADA, sources, confidentialité, API, Claude, Gemini et limites juridiques.
---

# Questions fréquentes sur OHADA MCP Server

## Qu'est-ce que OHADA MCP Server ?

OHADA MCP Server est un **serveur Model Context Protocol (MCP) public et open source** qui fournit à des assistants IA et applications LegalTech des outils structurés pour rechercher le droit OHADA, récupérer des articles complets, vérifier des citations et consulter le SYSCOHADA.

## OHADA MCP est-il un produit officiel de l'OHADA ?

Non. Il s'agit d'une initiative indépendante créée par **Christ Chadrak Mvoungou**. Le projet n'est pas encore affilié ou approuvé officiellement par l'institution OHADA.

## Est-ce une API pour le droit OHADA ?

Le projet expose un endpoint **MCP Streamable HTTP**, plutôt qu'une API REST traditionnelle. Un client compatible MCP découvre automatiquement les outils et leurs paramètres. Une application Python ou un agent peut donc l'utiliser comme couche d'accès structurée au corpus OHADA.

## Peut-on connecter OHADA MCP à Claude ?

Oui. Claude peut utiliser l'endpoint distant comme connecteur MCP lorsqu'il prend en charge les connecteurs personnalisés. Le [guide de connexion à Claude](integrations/claude.md) décrit la procédure.

## Peut-on utiliser OHADA MCP avec Gemini ou un autre agent IA ?

Oui, si l'environnement utilisé sait se connecter à un serveur **Model Context Protocol** distant en Streamable HTTP. Le serveur n'est pas lié à un seul modèle : il fournit les outils et les données, tandis que le client ou le modèle produit la synthèse.

## Pourquoi `/mcp` affiche-t-il une erreur dans mon navigateur ?

Parce qu'il s'agit d'un endpoint protocolaire, pas d'une page HTML. Utilisez un client MCP. La disponibilité se vérifie sur [`/health`](https://ohada-mcp-oa42gsj75q-ew.a.run.app/health).

## Faut-il une clé API ?

Non. Le niveau public actuel est anonyme et en lecture seule.

## Le serveur répond-il lui-même aux questions juridiques ?

Non. OHADA MCP fournit des outils et des données structurées. Claude, Gemini ou votre propre agent choisit les outils puis rédige la synthèse. Cette séparation permet de récupérer le texte et sa source avant la génération de la réponse.

## Quelle différence entre recherche et récupération ?

La recherche renvoie des candidats compacts. La récupération renvoie le texte complet et ses métadonnées officielles. Une réponse juridique finale doit reposer sur la récupération complète plutôt que sur un extrait de recherche seul.

## Quels textes OHADA sont indexés ?

Le corpus contient actuellement **13 textes juridiques OHADA**, ainsi que la publication officielle SYSCOHADA. La liste détaillée des textes, codes et versions se trouve dans la page [Corpus OHADA et SYSCOHADA](corpus.md).

## La jurisprudence CCJA est-elle disponible ?

Pas encore. Le serveur ne doit donc pas inventer d'exemples jurisprudentiels pour compléter une notion ouverte absente des textes. La jurisprudence CCJA et nationale fait partie des limites actuelles du corpus.

## Le SYSCOHADA est-il inclus ?

Oui. Trois outils dédiés permettent de rechercher des concepts, récupérer des passages complets et consulter un compte exact avec les pages et le contexte disponibles.

## Mes questions sont-elles enregistrées ?

L'application ne conserve ni historique, ni texte de question, ni termes de recherche dans une base applicative. Votre assistant IA reste cependant un service distinct avec sa propre politique de confidentialité.

## Puis-je utiliser OHADA MCP dans une application commerciale ?

Le code du serveur est publié sous licence MIT. Vérifiez séparément les conditions applicables aux sources documentaires, aux services tiers et au modèle IA utilisé par votre application.

## OHADA MCP remplace-t-il un avocat, juriste ou expert-comptable ?

Non. Le serveur facilite la recherche et la récupération documentaire. Une réponse générée par un assistant IA ne remplace pas l'analyse d'un professionnel, en particulier lorsque la jurisprudence, les faits du dossier, une version historique ou une interprétation sont déterminants.

## Comment contribuer ?

Le code source est public sur GitHub. Ouvrez une issue pour une amélioration fonctionnelle ou une anomalie non sensible. Utilisez le signalement privé GitHub pour toute vulnérabilité exploitable.
