# Outils SYSCOHADA

Ces outils interrogent la publication officielle du SYSCOHADA avec ses pages, classes, comptes et sous-sections.

## `search_syscohada`

Découvre des passages à partir de concepts comptables.

| Paramètre | Type | Obligatoire | Description |
|---|---|---:|---|
| `query` | string | oui | Concept comptable ciblé en français |
| `max_results` | integer | non | 1 à 10, valeur par défaut : 5 |
| `account_filter` | string | non | Compte de 2 à 4 chiffres, par exemple `101` |
| `class_filter` | string | non | Classe sur un chiffre, par exemple `1` |

```json title="Arguments"
{
  "query": "capital social apports associés",
  "max_results": 5,
  "account_filter": "101"
}
```

Chaque résultat contient un `chunk_id`, un extrait, les pages et, lorsqu'ils sont identifiés, le compte et la classe.

Un extrait sert uniquement à choisir les passages pertinents. Il ne suffit pas à fonder une affirmation comptable finale.

## `get_syscohada_passages`

Récupère le texte complet de **1 à 5 passages** identifiés par `search_syscohada`.

```json title="Arguments"
{
  "chunk_ids": [1265, 1267]
}
```

La réponse fournit pour chaque passage :

- le texte complet ;
- les pages de début et de fin ;
- la classe et le compte éventuels ;
- la sous-section, par exemple `Commentaires` ou `Fonctionnement` ;
- une citation prête à l'emploi ;
- la source officielle.

## `get_syscohada_account`

Retourne en un appel tous les passages indexés associés à un compte exact.

```json title="Arguments"
{"account_code": "101"}
```

Utilisez directement cet outil lorsque le numéro du compte est au centre de la question. Il évite une recherche suivie de plusieurs récupérations.

## Choisir le bon parcours

| Question | Parcours recommandé |
|---|---|
| « Comment fonctionne le compte 101 ? » | `get_syscohada_account` |
| « Quel compte traite les subventions d'investissement ? » | `search_syscohada` puis `get_syscohada_passages` |
| « Compare le compte 101 avec une règle de l'AUDCIF » | Outils SYSCOHADA et outils juridiques |

!!! info "Nature de la source"
    Les résultats SYSCOHADA proviennent de la publication officielle adoptée le 26 janvier 2017, publiée le 15 février 2017 et applicable depuis le 1er janvier 2018 pour les comptes personnels.
