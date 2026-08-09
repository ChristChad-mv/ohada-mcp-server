# Outils juridiques

Les huit outils de cette page couvrent la découverte, la récupération exacte, les métadonnées et les contrôles de citation ou de date.

## `search_ohada_law`

Découvre des dispositions candidates. La réponse contient des références et des extraits courts, jamais le texte complet faisant autorité pour la synthèse finale.

| Paramètre | Type | Obligatoire | Description |
|---|---|---:|---|
| `query` | string | oui | Concepts juridiques ciblés en français |
| `max_results` | integer | non | 1 à 10, valeur par défaut : 5 |
| `act_filter` | string | non | Code canonique, par exemple `AUSCGIE` |

```json title="Arguments"
{
  "query": "révocation judiciaire gérant associé minoritaire",
  "max_results": 5,
  "act_filter": "AUSCGIE"
}
```

Chaque résultat comprend notamment `act_code`, `article_reference`, `hierarchy_path` et `snippet`. Récupérez ensuite les articles retenus.

## `get_article`

Retourne un article exact et complet avec sa hiérarchie, sa version, ses dates d'effet et sa source officielle.

| Paramètre | Type | Obligatoire | Exemple |
|---|---|---:|---|
| `act_code` | string | oui | `AUSCGIE` |
| `article_reference` | string | oui | `326`, `655-1`, `27 ter` |

```json title="Arguments"
{
  "act_code": "AUSCGIE",
  "article_reference": "326"
}
```

Les références complexes sont acceptées lorsqu'elles existent dans le corpus. Une référence fictive n'est pas corrigée silencieusement.

## `get_articles`

Récupère **2 à 5 articles distincts** en un seul appel. Utilisez-le dès que plusieurs dispositions sont nécessaires.

```json title="Arguments"
{
  "articles": [
    {"act_code": "AUPCAP", "article_reference": "2"},
    {"act_code": "AUPCAP", "article_reference": "25"}
  ]
}
```

La réponse isole les références introuvables dans `errors` sans supprimer les articles valides de `articles`.

## `get_act`

Retourne les métadonnées générales d'un texte : nom officiel, année, date d'effet, description, nombre d'articles et source.

```json
{"act_code": "AUPCAP"}
```

Cet outil décrit l'acte ; il ne retourne pas tous ses articles.

## `list_legal_texts`

Retourne le catalogue compact des textes indexés. Aucun paramètre n'est requis.

```json
{}
```

Utilisez cet outil pour répondre à une question de couverture ou découvrir un code canonique.

## `get_version`

Retourne les métadonnées de la version actuellement indexée.

```json
{"act_code": "AUSCGIE"}
```

!!! warning "Limite temporelle"
    Le résultat n'est pas encore un historique exhaustif de tous les libellés antérieurs.

## `get_provision_at_date`

Contrôle si la version indexée d'un article était applicable à une date ISO.

| Paramètre | Type | Exemple |
|---|---|---|
| `act_code` | string | `AUSCGIE` |
| `article_reference` | string | `326` |
| `target_date` | string | `2018-03-12` |

```json
{
  "act_code": "AUSCGIE",
  "article_reference": "326",
  "target_date": "2018-03-12"
}
```

La réponse ne répète pas le texte. Appelez `get_article` si son contenu est aussi nécessaire.

## `verify_citation`

Vérifie et normalise une citation fournie par l'utilisateur.

```json
{"citation_text": "Article 326 AUSCGIE"}
```

La réponse indique notamment `is_valid`, `canonical_citation`, `act_code`, `article_reference`, `version` et l'URL officielle. Elle ne renvoie pas le texte complet.

!!! tip "Quand ne pas l'utiliser"
    N'appelez pas `verify_citation` après un `get_article` ou `get_articles` réussi pour la même référence : la récupération exacte a déjà établi son existence.
