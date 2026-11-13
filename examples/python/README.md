# Calculer et vérifier une empreinte SHA-256

Cet exemple lit les octets d’un fichier et affiche leur empreinte SHA-256. Il fonctionne avec un PDF comme avec tout autre fichier régulier. Il ne modifie pas le contenu, ne crée aucun fichier et n’utilise aucun service réseau.

Prérequis : Python 3.10 ou supérieur sur un système POSIX. Aucune dépendance Python externe. Essais réalisés avec Python 3.12.3 et comparaison indépendante avec OpenSSL 3.0.13.

## Calculer une empreinte

Depuis la racine du dépôt :

```bash
python3 examples/python/sha256_file.py README.md
```

La sortie est une ligne de 64 caractères hexadécimaux. Pour utiliser un document de test, remplacer `README.md` par son chemin, entre guillemets s’il comporte des espaces.

Le script lit le fichier par blocs de 1 Mio avec `hashlib.sha256()` et `update()`, puis obtient sa représentation hexadécimale par `hexdigest()`. Voir la [documentation officielle de hashlib](https://docs.python.org/3/library/hashlib.html), consultée le 11 novembre 2026.

## Comparer à une référence

Une référence doit provenir d’une source à laquelle vous faites confiance. Pour observer le mécanisme, créer un petit fichier local dont les trois octets sont exactement `abc`, sans saut de ligne :

```bash
mkdir -p .local/dz-sign/hashing
printf 'abc' > .local/dz-sign/hashing/message.txt
python3 examples/python/sha256_file.py .local/dz-sign/hashing/message.txt --expect ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

Le résultat indique que l’empreinte correspond. Modifier ensuite le contenu :

```bash
printf 'abd' > .local/dz-sign/hashing/message.txt
python3 examples/python/sha256_file.py .local/dz-sign/hashing/message.txt --expect ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

Cette fois, le script affiche l’empreinte calculée et signale une différence. Ces commandes écrasent uniquement le fichier d’exercice `message.txt` ; utiliser un autre nom si vous l’avez déjà employé pour vos propres données. Le répertoire est ignoré par Git.

La référence accepte les lettres hexadécimales en minuscules ou majuscules, sans préfixe ni espaces. La comparaison utilise [`hmac.compare_digest`](https://docs.python.org/3/library/hmac.html#hmac.compare_digest) ; cela ne transforme pas l’empreinte publique en authentification par clé secrète.

| Code de sortie | Signification |
|---|---|
| `0` | Calcul réussi ; si une référence est fournie, elle correspond |
| `1` | Calcul réussi, mais empreinte différente |
| `2` | Arguments incorrects ou lecture impossible |

## Ce que le résultat permet de dire

La différence établit que les données lues ne correspondent pas à cette référence. Elle ne permet pas d’en attribuer la cause : modification volontaire, copie différente ou simple saut de ligne, par exemple. Une correspondance ne vérifie ni une signature, ni un certificat, ni une identité. Pour ces distinctions, lire la [fiche de vérification](../../docs/cryptography/signature-validation.md).

Le script refuse les répertoires et les fichiers spéciaux. Un lien symbolique vers un fichier régulier est suivi. Il détecte certains changements pendant la lecture grâce à la taille et aux métadonnées ; ce contrôle ne garantit pas une photographie atomique d’un fichier modifié en parallèle. Pour un résultat interprétable, travailler sur une copie stable.

## Vérifier l’exemple

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples/python -p 'test_*.py' -v
```

Les tests couvrent les valeurs connues du fichier vide et de `abc`, la modification du contenu, les références mal formées, les entrées absentes ou non régulières et la lecture binaire sur plusieurs blocs. OpenSSL fournit la comparaison indépendante du dernier cas ; ce contrôle est signalé comme ignoré si l’outil manque.
