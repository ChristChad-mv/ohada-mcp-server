# Questions fréquentes

## OHADA MCP est-il un produit officiel de l'OHADA ?

Non. Il s'agit d'une initiative indépendante créée par Christ Chad. Le projet n'est pas encore affilié ou approuvé officiellement par l'institution OHADA.

## Pourquoi `/mcp` affiche-t-il une erreur dans mon navigateur ?

Parce qu'il s'agit d'un endpoint protocolaire, pas d'une page HTML. Utilisez un client MCP. La disponibilité se vérifie sur [`/health`](https://ohada-mcp-oa42gsj75q-ew.a.run.app/health).

## Faut-il une clé API ?

Non. Le niveau public actuel est anonyme et en lecture seule.

## Le serveur répond-il lui-même aux questions ?

Non. OHADA MCP fournit des outils et des données structurées. Claude, Gemini ou votre propre agent choisit les outils puis rédige la synthèse.

## Quelle différence entre recherche et récupération ?

La recherche renvoie des candidats compacts. La récupération renvoie le texte complet et ses métadonnées officielles. Une réponse juridique finale doit reposer sur la récupération complète.

## La jurisprudence est-elle disponible ?

Pas encore. Le serveur ne doit donc pas inventer d'exemples jurisprudentiels pour compléter une notion ouverte absente des textes.

## Le SYSCOHADA est-il inclus ?

Oui. Trois outils dédiés permettent de rechercher des concepts, récupérer des passages complets et consulter un compte exact.

## Mes questions sont-elles enregistrées ?

L'application ne conserve ni historique, ni texte de question, ni termes de recherche. Votre assistant IA reste cependant un service distinct avec sa propre politique.

## Puis-je utiliser OHADA MCP dans une application commerciale ?

Le code du serveur est publié sous licence MIT. Vérifiez séparément les conditions applicables aux sources documentaires, aux services tiers et au modèle IA utilisé par votre application.

## Comment contribuer ?

Après publication du dépôt, ouvrez une issue pour une amélioration fonctionnelle ou une anomalie non sensible. Utilisez le signalement privé GitHub pour toute vulnérabilité exploitable.
