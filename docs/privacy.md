# Confidentialité

## Ce que reçoit OHADA MCP

Le client MCP choisit les arguments envoyés à chaque outil : termes de recherche, code d'acte, référence d'article, date, numéro de compte ou identifiants de passages. Il n'est pas nécessaire que le serveur reçoive l'intégralité de la conversation tenue avec votre assistant.

## Ce que le serveur ne conserve pas

L'application OHADA MCP :

- ne crée pas d'historique de conversation ;
- n'enregistre pas le texte des questions ou des recherches ;
- n'écrit pas les arguments des outils dans ses journaux applicatifs ;
- n'utilise pas les questions pour entraîner un modèle ;
- ne crée pas de profil utilisateur.

Les arguments sont traités en mémoire le temps nécessaire à la réponse. La limitation de débit conserve uniquement un identifiant réseau HMAC éphémère pendant une courte fenêtre. Cet identifiant n'est ni un texte de question ni une adresse IP conservée en clair.

## Journaux d'infrastructure

La plateforme d'hébergement peut conserver des métadonnées techniques de requête nécessaires à l'exploitation et à la sécurité—par exemple l'heure, le chemin, le statut HTTP ou la latence. L'application désactive ses journaux d'accès et ne transmet pas le corps des requêtes à ces métriques.

## Votre assistant reste un service distinct

Claude, Gemini ou tout autre client peut appliquer sa propre politique de conservation. OHADA MCP ne contrôle pas cette partie du traitement.

!!! danger "Ne transmettez pas de dossier confidentiel"
    Le serveur est destiné à des recherches juridiques générales. N'envoyez pas de dossier client, pièce confidentielle, donnée personnelle, secret professionnel ou identifiant d'accès.
