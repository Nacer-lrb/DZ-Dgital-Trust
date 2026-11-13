# Développement et contribution

[Manuel](README.md) · [English](../en/development.md) · [العربية](../ar/development.md)

## Structure du code

`demo/backend/app/` contient les routes HTTP, le stockage temporaire, le protocole des processus et leur configuration. `examples/` contient les opérations cryptographiques et leurs exercices. L’interface distingue les contrats JSON, le transport HTTP, le registre et le rendu du rapport.

Les versions sont fixées dans les fichiers de dépendances. Ne pas modifier les paquets installés ou les fichiers de framework générés pour contourner une erreur. Les clés et documents locaux restent dans `.local/dz-sign/`, exclu par `.gitignore` lors d’une éventuelle initialisation du dépôt.

## Contrôles

Après installation des dépendances de développement :

```bash
python3 scripts/check.py
```

Cette commande exécute les tests Python, l’analyse et le formatage de contrôle, puis les vérifications frontend et la compilation. OpenSSL doit être installé pour les contrôles indépendants ; sans lui, certains tests annoncent leur omission.

Pour reformater le code :

```bash
.local/dz-sign/venv/bin/ruff format demo/backend examples scripts
cd demo/frontend
npm run format
```

Les tests couvrent les clés chiffrées, les empreintes connues, les chaînes, les PDF altérés ou hybrides, les expirations, les origines HTTP et le nettoyage des processus. Ajouter un test pour un défaut reproductible ou un changement de contrat, pas pour recopier l’implémentation.

## Attentes de revue

Décrire le problème, le comportement obtenu et les contrôles exécutés. Employer des messages de commit en anglais si un historique est créé. Une modification de limite, de route ou de traitement des données doit être répercutée dans les trois manuels. Les limites de sécurité doivent rester visibles ; ne jamais transformer un résultat indéterminé en succès.

La licence MIT concerne les contributions d’origine. Respecter les [mentions tierces](../../THIRD_PARTY_NOTICES.md) et ne pas ajouter de document personnel, de clé privée ou de secret aux fichiers destinés à être partagés.
