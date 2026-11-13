# Installation et exploitation locale

[Manuel](README.md) · [English](../en/installation.md) · [العربية](../ar/installation.md)

## Prérequis

Linux ou un environnement POSIX, Python 3.12, Node.js 22 ou supérieur et npm. OpenSSL 3 est nécessaire aux contrôles cryptographiques indépendants. Les dépendances sont téléchargées pendant l’installation ; le parcours PDF fonctionne ensuite sans récupération réseau automatique.

Depuis la racine du projet :

```bash
python3 -m venv .local/dz-sign/venv
.local/dz-sign/venv/bin/python -m pip install -r demo/backend/requirements-dev.txt
.local/dz-sign/venv/bin/python demo/backend/setup_demo.py
```

Si l’environnement existe, ne pas le recréer. Le script de préparation crée une identité fictive dans `.local/dz-sign/app-identity/` et refuse d’écraser une identité existante. Son certificat de signature dure trente jours. Pour une autre génération, utiliser `--output` avec un nouveau répertoire et configurer `DZ_SIGN_IDENTITY_DIR`.

## Démarrage

Premier terminal, à la racine :

```bash
.local/dz-sign/venv/bin/python -m uvicorn app.main:app --app-dir demo/backend --host 127.0.0.1 --port 8000
```

Second terminal :

```bash
cd demo/frontend
npm ci
npm run dev
```

Ouvrir `http://127.0.0.1:3000`. L’état de l’API se trouve à `http://127.0.0.1:8000/api/health` et son contrat à `/docs`. Après une modification du backend, le redémarrer. Arrêter chaque service avec `Ctrl+C`.

## Configuration

| Variable | Valeur par défaut |
|---|---|
| `DZ_SIGN_FRONTEND_ORIGIN` | `http://127.0.0.1:3000` |
| `NEXT_PUBLIC_API_ORIGIN` | `http://127.0.0.1:8000` |
| `DZ_SIGN_IDENTITY_DIR` | `.local/dz-sign/app-identity/`, résolu côté serveur |
| `DZ_SIGN_PASSWORD_FILE` | `runtime/signer.secret` de cette identité |

`localhost` et `127.0.0.1` sont des origines différentes. Les variables `NEXT_PUBLIC_*` sont publiques. Dans Next.js, leurs valeurs sont intégrées à la compilation : une modification exige une recompilation en mode production.

Une seule instance backend peut utiliser le stockage temporaire. Ne pas ajouter plusieurs workers et ne pas lier le service à `0.0.0.0` dans ce périmètre sans authentification.

## Diagnostic

| Symptôme | Vérification |
|---|---|
| Service inaccessible | API démarrée, bon port, bonne origine, versions serveur et interface cohérentes |
| Signature désactivée | Identité préparée, fichiers présents, clé et secret en `0600` |
| `409` | Traitement déjà actif ou deuxième instance utilisant le même stockage |
| `410` | Document expiré : le réimporter |
| `413` | Fichier ou copie signée dépassant 10 Mio |
| `422` | Lire le message : PDF chiffré, contenu non pris en charge, confirmation manquante ou configuration incorrecte |
| `504` | Délai de traitement dépassé ; fichiers partiels supprimés |

Un `OPTIONS 200` est une vérification CORS normale. Il ne prouve pas que la demande `POST` suivante aboutira.
