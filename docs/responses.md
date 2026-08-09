# Formats de réponse

Les outils retournent des objets structurés. Un client doit utiliser `structuredContent` plutôt que tenter d'extraire des valeurs depuis un texte affiché.

## Article juridique

```json
{
  "act_code": "AUSCGIE",
  "act_name": "Acte Uniforme — Sociétés Commerciales & GIE",
  "article_reference": "326",
  "version": "2014",
  "status": "in_force",
  "effective_from": "2014-05-05",
  "effective_until": null,
  "hierarchy_context": {
    "full_path": "Révocation > Article 326"
  },
  "text": "… texte normatif complet …",
  "official_source": {
    "publisher": "Secrétariat Permanent de l'OHADA",
    "publication": "Journal Officiel de l'OHADA …",
    "url": "https://www.ohada.org/…"
  }
}
```

## Résultat de recherche

Un résultat de recherche est volontairement compact :

```json
{
  "rank": 1,
  "act_code": "AUSCGIE",
  "article_reference": "326",
  "hierarchy_path": "Révocation > Article 326",
  "snippet": "Le gérant est révocable…"
}
```

Le champ `snippet` est une aide à la sélection, pas le substitut de `text`.

## Vérification de citation

```json
{
  "citation_text": "Article 326 AUSCGIE",
  "is_valid": true,
  "confidence": 1.0,
  "canonical_citation": "Article 326 AUSCGIE",
  "act_code": "AUSCGIE",
  "article_reference": "326",
  "version": "2014",
  "status": "in_force",
  "official_source_url": "https://www.ohada.org/…",
  "explanation": "Citation valide."
}
```

Cette réponse ne contient volontairement pas de copie de l'article.

## Passage SYSCOHADA

```json
{
  "chunk_id": 1267,
  "hierarchy_path": "Classe 1 > Compte 101 — Capital social > Fonctionnement",
  "text": "… passage complet …",
  "page_start": 277,
  "page_end": 277,
  "class_code": "1",
  "account_code": "101",
  "account_subsection": "Fonctionnement",
  "citation": "SYSCOHADA — compte 101, p. 277",
  "official_source": {
    "publisher": "Secrétariat Permanent de l'OHADA",
    "effective_from": "2018-01-01"
  }
}
```

Les numéros de `chunk_id` servent d'identifiants techniques de récupération. Pour une citation destinée au lecteur, utilisez le champ `citation` et les pages.
