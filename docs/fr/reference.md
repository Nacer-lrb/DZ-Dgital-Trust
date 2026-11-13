# Architecture, API et sécurité

[Manuel](README.md) · [English](../en/reference.md) · [العربية](../ar/reference.md)

## Composants

Next.js et React présentent les documents et les rapports. FastAPI contrôle l’origine navigateur, les imports et la durée de conservation. pyHanko exécute les opérations PDF dans des processus enfants. Les commandes et dépendances sont consignées dans les fichiers de versions du dépôt.

Le backend conserve les métadonnées en mémoire et les fichiers sous `.local/dz-sign/uploads/`. Un identifiant aléatoire désigne chaque document ; le nom reçu n’est jamais utilisé comme chemin de stockage. Il n’existe ni base de données, ni compte, ni reprise de session après redémarrage.

## Contrat HTTP

| Méthode et route | Corps ou résultat |
|---|---|
| `GET /api/health` | État et capacités réellement disponibles |
| `GET /api/documents` | Documents non expirés |
| `POST /api/documents` | Multipart : un fichier nommé `file` |
| `GET /api/documents/{id}` | Métadonnées et référence de la copie éventuelle |
| `GET /api/documents/{id}/download` | Original en pièce jointe |
| `POST /api/documents/{id}/sign` | `{"confirm_test_signature": true}` |
| `POST /api/documents/{id}/verify` | `{"source":"original"}` ou `{"source":"signed"}` |
| `GET /api/results/{id}/download` | Copie signée en pièce jointe |
| `DELETE /api/documents/{id}` | Suppression de l’original et de sa copie |

Un rapport produit reçoit HTTP `200`, même si son `outcome` signale un échec cryptographique. Les erreurs de requête et les traitements impossibles sont distincts. La réponse de signature indique `normalized_before_signing` si la structure d’un PDF hybride a été réécrite.

## Limites appliquées

| Ressource | Limite |
|---|---|
| Fichier ou copie publiée | 10 Mio |
| Enveloppe multipart | 10 Mio + 64 Kio, vérifiée pendant la lecture |
| Documents | Dix, soit au plus 200 Mio d’originaux et de copies |
| Traitements actifs | Un |
| Durée | 30 secondes par import, signature ou vérification |
| Processus PDF | 512 Mio d’espace virtuel, 30 secondes CPU sur POSIX |
| Sortie d’un rapport | 2 Mio |
| Conservation | Quinze minutes maximum depuis le début de l’import |

L’expiration est contrôlée avant l’accès. Un traitement actif garde son fichier jusqu’à l’arrêt du processus, mais son résultat expiré n’est pas publié. Le nettoyage passe chaque minute, à l’arrêt normal et au démarrage. Une horloge monotone empêche un recul de l’heure système de prolonger la conservation.

## Frontières de confiance

Les clés de test sont chiffrées en PKCS#8. Clés et secrets sont privés (`0600`), les dossiers documentaires en `0700`. Les chemins de clé, de secret et de racine sont définis par le serveur ; aucun endpoint ne permet de les choisir. Le navigateur ne reçoit aucun secret.

Les workers n’effectuent pas de récupération réseau automatique. Le protocole parent-enfant est JSON, borné et vérifié ; une sortie illisible est rejetée, jamais assimilée à une réussite.

Les contrôles d’origine et de Host ne constituent pas une authentification. La version est destinée à un utilisateur local. Les restrictions applicatives ne sont pas un bac à sable système complet ; une personne ayant accès au même compte peut lire le stockage. Le service ne garantit pas un effacement forensique.

## Interface

Le registre et le panneau de traitement sont séparés du rapport. Les pages méthode, confidentialité et conditions d’utilisation sont des routes réelles. Les états de chargement, erreur, absence de document et expiration sont explicites. Aucune métrique, démonstration ou donnée documentaire n’est inventée pour remplir l’écran.
