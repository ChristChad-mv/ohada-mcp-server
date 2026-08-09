# Contribuer à OHADA MCP

Merci de contribuer à rendre l'information juridique OHADA plus accessible et plus fiable.

## Contributions bienvenues

- fiabilité du serveur et interopérabilité MCP ;
- schémas, validation et gestion des erreurs ;
- documentation et exemples d'intégration ;
- couverture de tests ;
- accessibilité et corrections linguistiques ;
- signalements reproductibles d'erreurs de corpus accompagnés d'une source officielle.

Les bases de production et les opérations d'ingestion ne font pas partie du périmètre de ce dépôt public.

## Environnement de développement

Installez [`uv`](https://docs.astral.sh/uv/getting-started/installation/), puis exécutez :

```bash
uv sync --locked --extra dev --extra docs
uv run pytest -q
uv run ruff check src tests scripts
uv run mkdocs build --strict
```

Les tests créent un corpus temporaire minimal et ne doivent jamais dépendre d'une base de production.

## Pull requests

Créez une branche dédiée et gardez chaque changement ciblé. Ajoutez des tests lorsqu'un comportement change et mettez la documentation à jour lorsqu'un contrat public évolue. Les checks CI doivent être verts avant la fusion ; l'historique de `master` utilise le squash merge.

Ne commitez jamais de base générée, PDF source, identifiant, état Terraform, poids de modèle, requête utilisateur ou document client.

## Corrections du corpus

Indiquez le code du texte, la référence de l'article, le texte observé, le texte attendu, l'URL de la publication officielle et sa date. Un court extrait reproductible suffit ; ne recopiez pas une publication entière.

## Communication responsable

Ne présentez pas le projet comme un service officiel de l'OHADA et ne transmettez aucune donnée juridique personnelle ou confidentielle. Signalez les vulnérabilités en suivant [`SECURITY.md`](SECURITY.md), jamais dans une issue publique.
