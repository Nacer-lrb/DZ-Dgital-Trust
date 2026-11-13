# Direction de l’interface DZ Sign

Date : 13 novembre 2026. Cette direction reprend la demande explicite du projet : une interface professionnelle, distinctive et centrée sur des opérations réelles.

## Un espace documentaire

L’écran principal présente un registre de documents disponibles dans l’instance locale et un panneau de traitement. Le nom du document sélectionne son contexte ; les actions portent toujours sur cet original ou sur sa copie signée identifiée. Le rapport distingue les contrôles et peut être exporté. Aucun contenu documentaire n’est ajouté artificiellement pour remplir l’écran vide.

La navigation donne accès à la méthode de vérification. Les liens de confidentialité et de conditions d’utilisation restent accessibles dans le pied de page. Les commandes de démarrage se trouvent dans le guide, plutôt que dans le parcours courant.

## Identité visuelle retenue

- Fond papier minéral, encre sombre, accent terre cuite pour les actions principales.
- Typographie système sans dépendance de police distante ; chiffres techniques à largeur stable quand ils facilitent la lecture.
- Espacements réguliers, filets fins et coins presque droits.
- Tableau pour les documents, définitions pour les métadonnées, tableau de contrôles pour les signatures.
- Couleurs de statut employées pour leur sens, jamais pour décorer une succession de blocs.

## Éléments exclus

Pas de dégradés, de fond blanc pur, d’effets de verre, d’ombres décoratives, d’orbes ou de grilles de points. Pas de grille bento, de séries de cartes de fonctionnalités, de démonstrations fictives, de témoignages ou de tarification sans rapport avec le produit. Pas d’emojis comme icônes, de collection d’icônes génériques, de polices Inter, Geist ou Space Grotesk, ni d’animations d’ornement.

## États et accessibilité

Le chargement initial dispose d’un état squelettique statique. Les opérations longues utilisent une progression indéterminée, sans pourcentage inventé. Les états vide, hors connexion, erreur, document expiré et identité non configurée indiquent une action possible.

Les contrôles sont des éléments HTML natifs avec libellés, le tableau dispose d’en-têtes, les messages importants sont annoncés et le focus rejoint le rapport après une vérification. La signature demande une confirmation explicite. Les téléchargements correspondent à de vrais fichiers et rapports.

Sur mobile, les zones de travail se suivent en une colonne. Aucun contrôle essentiel ne dépend d’un survol. Toute future composante doit apporter une fonction identifiable avant son ajout.
