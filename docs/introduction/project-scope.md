# Périmètre de DZ Digital Trust

DZ Digital Trust associe une documentation sur la confiance numérique et une application locale, DZ Sign. Les [manuels français, anglais et arabe](../README.md) décrivent la version disponible.

## Public et usage

Le projet s’adresse aux développeurs, ingénieurs et étudiants qui souhaitent examiner les mécanismes de signature PDF dans le contexte algérien. Il utilise des documents fictifs et des identités de test ; il ne fournit aucun service accrédité.

## Parcours disponible

Une personne importe un PDF, consulte ses métadonnées et peut signer une copie. Le vérificateur analyse l’original ou la copie, en distinguant intégrité, certificat, période et couverture. Les fichiers et rapports peuvent être téléchargés avant leur expiration.

L’application conserve les documents pendant quinze minutes au maximum. Elle n’utilise ni compte utilisateur, ni base de données, ni stockage durable. Le cachet et les circuits d’approbation restent hors de cette version.

## Critères de fonctionnement

| Situation | Comportement attendu |
|---|---|
| PDF lisible | Import et empreinte du fichier reçu |
| PDF chiffré ou illisible | Refus explicite |
| Signature de test | Copie séparée et original intact |
| PDF hybride non signé | Réécriture de la copie signalée avant signature |
| Données couvertes altérées | Contrôle d’intégrité en échec |
| Racine non approuvée | Confiance non établie, distincte de l’intégrité |
| Contrôle indisponible | Résultat non vérifié ou indéterminé |
| Expiration ou suppression | Original et copie retirés du service |

## Limites

Le projet vise PAdES-B-B sans affirmer une conformité exhaustive. La révocation, l’horodatage de confiance, la validité historique et la qualification juridique ne sont pas établis. Les études institutionnelles ne certifient pas l’achèvement d’une transition réglementaire.

L’[architecture](../architecture/dz-sign.md), la [gestion des clés](../architecture/key-management.md) et le [registre des références](../../resources/references.md) précisent les décisions techniques et les questions ouvertes.
