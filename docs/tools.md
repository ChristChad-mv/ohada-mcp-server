# Référence des outils

## `search_ohada_law`

Recherche textuelle de découverte dans les textes indexés. La réponse contient des références et des extraits courts (600 caractères par défaut), pas le texte complet. Une disposition retenue doit ensuite être récupérée avec `get_article` ou `get_articles`.

| Argument | Type | Description |
|---|---|---|
| `query` | string | Termes ou question en français |
| `max_results` | integer | 1 à 10, valeur par défaut 5 |
| `act_filter` | string ou null | Code canonique, par exemple `AUSCGIE` |

## `get_article`

Retourne le texte, la hiérarchie, la version indexée, la date d'effet et la source officielle d'un article.

## `get_articles`

Retourne les textes complets de 2 à 5 articles exacts en un seul appel. Cet outil réduit les allers-retours lorsqu'une réponse dépend de plusieurs dispositions. Une erreur sur une référence n'empêche pas le retour des autres articles valides.

## `get_act`

Retourne les métadonnées du texte correspondant à un code canonique.

## `list_legal_texts`

Retourne un catalogue compact des textes actuellement couverts. Utiliser `get_act` pour les métadonnées détaillées d'un texte.

## `get_version`

Retourne les métadonnées de la version actuellement indexée. Cet outil ne constitue pas encore un historique exhaustif des versions antérieures.

## `get_provision_at_date`

Compare une date ISO `YYYY-MM-DD` avec la période d'effet de la version indexée. La réponse est compacte et ne répète pas l'article. Il ne reconstitue pas encore un ancien libellé remplacé.

## `verify_citation`

Reconnaît les citations contenant un code canonique, comme `Article 326 AUSCGIE`, ainsi que certains intitulés officiels contrôlés. La réponse confirme et normalise la référence sans renvoyer une seconde fois le texte complet. Pour une question juridique de fond, utiliser directement `get_article`.
