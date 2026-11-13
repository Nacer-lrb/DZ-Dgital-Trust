# Clés de test et limites de sécurité

Où sera conservée la clé qui signe les PDF ? Qui pourra l’utiliser ? Cette fiche fixe les règles du prototype local avant la génération de certificats et l’écriture du backend.

Décisions du projet au **11 novembre 2026**, complétées le **13 novembre 2026**. Le parcours de signature de l’application utilise désormais une identité fictive configurée côté serveur, des clés chiffrées et un secret en fichier privé. Les tests de ce parcours sont décrits dans `demo/README.md`. Voir l’[architecture](dz-sign.md) et la [fiche PKI](../cryptography/pki.md).

## Des identités explicitement fictives

Les exemples créeront une autorité racine de test, une autorité intermédiaire et un certificat de signature portant un libellé tel que « Amel — TEST ». Les certificats et leur documentation devront indiquer leur usage pédagogique.

Le choix initial est de générer les clés sur la machine de la personne qui lance les exemples. Aucune clé privée préfabriquée ne sera distribuée dans le dépôt. Le [premier exemple exécutable](../../examples/certificate-generation/README.md) fixe les paramètres du laboratoire : RSA 3072, SHA-256, durées de 365, 180 et 30 jours. Il génère des clés chiffrées et des certificats dont la chaîne est contrôlée par OpenSSL dans les tests. Le backend applique des limites de traitement, des contrôles d’origine et un nettoyage temporaire ; les restrictions applicatives ne constituent pas un bac à sable système complet.

## Séparer les rôles des clés

| Élément | Emplacement prévu | Accès du backend |
|---|---|---|
| Clé privée racine | Répertoire local de génération | Aucun |
| Clé privée intermédiaire | Répertoire local de génération | Aucun |
| Clé privée de signature | Répertoire local d’exécution | Lecture pour la signature de test |
| Certificat du signataire et intermédiaires | Configuration locale d’exécution | Lecture pour joindre la chaîne et vérifier |
| Certificat racine approuvé | Configuration de confiance distincte | Lecture pour la validation |

Les chemins ne seront pas fournis par les requêtes HTTP. En conteneur, seuls les éléments d’exécution nécessaires seront montés en lecture seule ; les clés des autorités resteront hors du conteneur. Elles ne seront nécessaires que pour les opérations explicites de délivrance et de révocation dans les exemples.

## Stockage et secrets

Nous réservons `.local/dz-sign/` aux données générées : sous-répertoires de génération, d’exécution et de travail temporaire. Ce répertoire sera ignoré par Git. Les exemples devront créer les dossiers privés avec le mode `0700` et les fichiers de clés avec le mode `0600`, ou des protections équivalentes sur le système utilisé.

Les clés sont stockées sous forme PKCS#8 chiffrée. La phrase secrète est saisie à la demande pour les exemples ; le backend utilise un fichier secret local protégé dont le chemin est configuré côté serveur. Le script `demo/backend/setup_demo.py` prépare l’identité de l’application sous `.local/dz-sign/app-identity/`, avec un secret de signataire dans `runtime/signer.secret` et un secret d’autorités séparé dans `generation/authority.secret`. Le processus de signature charge uniquement le premier. Aucun secret n’est transmis au navigateur, utilisé comme valeur d’argument de commande ou écrit dans les rapports.

Cette protection limite l’exposition sur disque ; elle ne protège pas contre la compromission du processus qui utilise la clé. Une clé déchiffrée pourra être présente en mémoire pendant l’opération. Le prototype ne prétendra pas fournir l’isolation d’un matériel dédié.

L’exclusion Git est une précaution de rangement, pas une garantie de confidentialité. Avant chaque commit des exemples, les chemins ajoutés devront être examinés pour éviter toute clé ou donnée de test locale involontairement incluse.

## Encadrer l’entrée et le traitement des PDF

Le nom et le type déclarés par le navigateur ne seront pas considérés comme une validation du contenu. Le backend contrôlera la taille, fera analyser le fichier et refusera les PDF chiffrés nécessitant un mot de passe dans le premier parcours. Les téléchargements seront servis comme pièces jointes. Aucune prévisualisation active de contenu PDF n’est prévue initialement.

Le processus de traitement devra fonctionner sans droits administrateur, avec accès limité à son répertoire de travail et aux éléments cryptographiques nécessaires. Le délai de 30 secondes protège le service d’un blocage prolongé ; il ne remplace pas une limite mémoire. Le guide d’exécution devra fixer une limite mémoire adaptée après les mesures réalisées sur les fixtures.

Ces mesures ne constituent pas une isolation complète contre un PDF malveillant. La démonstration restera locale et utilisera des documents fictifs. Le durcissement d’un service exposé devra être traité avant tout changement de mode de déploiement.

## Accès local et réseau

L’interface et l’API seront liées à l’interface de boucle locale. Aucun accès depuis le réseau local ne sera activé par défaut. L’API n’autorisera que l’origine exacte de l’interface configurée et vérifiera l’origine des requêtes provenant du navigateur ; une règle CORS permissive ne sera pas utilisée comme contrôle d’accès.

La vérification sera configurée sans récupération réseau automatique, notamment pour les certificats intermédiaires, les CRL, OCSP ou l’horodatage. Les références présentes dans un certificat ou un PDF ne devront déclencher aucune connexion. Les preuves manquantes resteront visibles dans le rapport. Une future fonction réseau nécessiterait une politique explicite de destinations, de limites et de délais.

## Incident et renouvellement

Si une clé de test est divulguée, elle sera retirée de la configuration de signature. Une nouvelle paire et un nouveau certificat seront générés. Dans les exemples dédiés à la révocation, le statut de l’ancien certificat sera publié dans les éléments de test et utilisé pour observer le comportement du vérificateur.

Les anciens certificats publics pourront être conservés avec les fixtures pour comprendre les résultats passés. Un certificat expiré ne sera pas modifié pour prolonger sa période : un nouveau certificat sera émis. La remise à zéro de l’environnement local devra être une commande explicite, avec un périmètre de suppression limité et documenté.

## Vérifications attendues avant livraison

- Aucune clé privée ni phrase secrète n’apparaît dans le dépôt, les réponses HTTP ou les journaux.
- Le backend ne peut pas charger les clés privées des autorités à partir de sa configuration d’exécution.
- Un nom de fichier ou un identifiant reçu ne permet pas d’accéder à un chemin arbitraire.
- Un import trop volumineux est interrompu ; un processus bloqué est arrêté et ses fichiers partiels sont nettoyés.
- Une URL présente dans les données reçues n’entraîne pas de connexion réseau automatique.
- Une preuve absente ne produit pas un contrôle favorable ; une racine reçue ne devient pas une ancre approuvée.

Ces points serviront aux essais d’implémentation. Ils ne sont pas présentés comme des garanties déjà établies par le dépôt documentaire.
