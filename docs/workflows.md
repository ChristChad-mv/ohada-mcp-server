# Enchaînements recommandés

Cette page explique comment un assistant ou un agent doit choisir et arrêter ses appels.

## Question juridique générale

```text
Question
  ↓
search_ohada_law
  ↓ sélection des dispositions nécessaires
get_article ou get_articles
  ↓
Synthèse fondée uniquement sur les textes complets
```

1. Rechercher les dispositions candidates.
2. Examiner les références et extraits retournés.
3. Récupérer l'unique article nécessaire avec `get_article`, ou 2 à 5 articles avec `get_articles`.
4. Répondre à partir des textes complets.
5. Arrêter les appels lorsque les sources nécessaires et suffisantes sont présentes.

## Référence exacte déjà connue

```text
« Que prévoit l'article 326 AUSCGIE ? »
  ↓
get_article
  ↓
Réponse
```

La recherche et la vérification de citation seraient redondantes.

## Citation possiblement fictive

Pour une demande purement formelle :

```text
« L'article 440-1 AUSCGIE existe-t-il ? »
  ↓
verify_citation
```

Pour une question de fond fondée sur cette référence :

```text
get_article échoue
  ↓
search_ohada_law sur le concept juridique
  ↓
récupération de la disposition réellement pertinente
  ↓
explication explicite de la correction
```

Ne remplacez jamais silencieusement une référence inexistante.

## Question temporelle

Utilisez `get_provision_at_date` pour contrôler la période d'effet de la version indexée. Complétez avec `get_article` uniquement si le texte est nécessaire à la réponse.

Le service ne reconstitue pas encore automatiquement le libellé historique d'une disposition remplacée.

## Question SYSCOHADA

```text
Compte exact indiqué ?
├─ Oui → get_syscohada_account
└─ Non → search_syscohada → get_syscohada_passages
```

## Question mixte

Une question peut nécessiter à la fois une disposition de l'AUDCIF et des passages du SYSCOHADA. Dans ce cas, récupérez séparément les sources complètes de chaque corpus, puis distinguez clairement leur rôle dans la réponse.

## Contrôle avant la réponse

Un agent fiable doit pouvoir répondre oui à ces questions :

- chaque règle juridique citée provient-elle d'un article complet récupéré ?
- chaque règle comptable provient-elle d'un passage complet avec ses pages ?
- les codes d'actes sont-ils recopiés exactement ?
- une condition soumise au juge est-elle présentée comme une condition, et non comme un résultat automatique ?
- les limites du corpus sont-elles signalées ?
