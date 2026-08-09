# Le droit OHADA, directement dans les assistants IA

OHADA MCP est un serveur public qui permet aux clients compatibles MCP de **rechercher les textes OHADA**, **récupérer des articles complets**, **contrôler des citations** et **consulter le SYSCOHADA**.

<div class="endpoint-card" markdown>

**Endpoint MCP public**

```text
https://ohada-mcp-oa42gsj75q-ew.a.run.app/mcp
```

[Se connecter en 5 minutes](quickstart.md){ .md-button .md-button--primary }
[Voir les 11 outils](tools.md){ .md-button }

</div>

!!! info "Initiative indépendante"
    OHADA MCP est créé par **Christ Chad**. Le projet n'est pas encore affilié, approuvé ou exploité officiellement par l'OHADA.

## Que voulez-vous faire ?

<div class="grid cards" markdown>

-   :material-robot-outline:{ .lg .middle } **Connecter un assistant**

    ---

    Ajoutez l'URL distante dans Claude ou dans un autre client MCP, puis posez directement vos questions.

    [:octicons-arrow-right-24: Démarrage rapide](quickstart.md)

-   :material-code-braces:{ .lg .middle } **Construire une LegalTech**

    ---

    Utilisez le SDK MCP pour découvrir les outils et exploiter leurs réponses structurées.

    [:octicons-arrow-right-24: Intégration Python](integrations/python.md)

-   :material-scale-balance:{ .lg .middle } **Interroger le droit OHADA**

    ---

    Recherchez une règle, récupérez le texte intégral de l'article et conservez sa source officielle.

    [:octicons-arrow-right-24: Outils juridiques](tools/legal.md)

-   :material-calculator-variant-outline:{ .lg .middle } **Consulter le SYSCOHADA**

    ---

    Recherchez un concept comptable ou récupérez directement le contexte complet d'un compte.

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

## Couverture actuelle

- 13 textes juridiques OHADA indexés ;
- Actes uniformes, Traité et règlements CCJA ;
- publication officielle SYSCOHADA avec pages et structure comptable ;
- métadonnées de version, dates d'effet et sources officielles.

La jurisprudence CCJA et nationale ainsi que le guide d'application SYSCOHADA ne sont pas encore intégrés. Consultez la page [Textes couverts](corpus.md) pour le détail.

## Garanties du service

OHADA MCP est en lecture seule. Il n'exécute pas de commandes, ne modifie pas les textes et n'accepte pas d'URL arbitraire. L'application ne conserve pas le texte des questions ou des recherches. Consultez les pages [Confidentialité](privacy.md) et [Sécurité](security.md).

!!! warning "Information juridique, pas conseil juridique"
    Les réponses d'un assistant restent des synthèses automatisées. Vérifiez la version applicable, la publication officielle et, lorsque nécessaire, la jurisprudence ou l'avis d'un professionnel qualifié.

Pour les assistants et agents automatisés, une synthèse machine-readable est disponible dans [`llms.txt`](llms.txt).
