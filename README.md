# DZ Digital Trust

Étude de la confiance numérique dans le contexte algérien, accompagnée de **DZ Sign**, une application locale de signature et de vérification PDF.

| Documentation | Accès |
|---|---|
| Français | [Manuel du projet](docs/fr/README.md) |
| English | [Project handbook](docs/en/README.md) |
| العربية | [دليل المشروع](docs/ar/README.md) |

## Ce qui fonctionne

- Import de PDF, consultation des métadonnées et empreinte SHA-256.
- Signature d’une copie avec une identité fictive ; conservation de l’original.
- Vérification de l’intégrité, du certificat et de la couverture de la signature.
- Rapports texte dans l’interface et export JSON.
- Suppression et expiration des documents après quinze minutes au maximum.

L’application utilise Next.js, React et TypeScript pour l’interface, FastAPI pour l’API et pyHanko pour les opérations PDF. Les exemples Python fonctionnent aussi en ligne de commande. Les versions exactes sont enregistrées dans les fichiers de dépendances.

Le cachet électronique, les circuits d’approbation, les comptes utilisateurs et la conservation durable ne sont pas implémentés. Cette version n’établit ni une qualification juridique, ni un statut de révocation, ni un horodatage de confiance.

## Organisation

| Chemin | Contenu |
|---|---|
| `demo/` | Application locale et tests d’intégration |
| `examples/` | Génération de certificats, hachage, signature et vérification |
| `docs/fr/`, `docs/en/`, `docs/ar/` | Manuels opérationnels et techniques équivalents |
| `docs/cryptography/`, `docs/standards/`, `docs/algeria/` | Études détaillées de référence, en français |
| `legal/` | Publication officielle utilisée pour l’étude juridique |
| `resources/` | Registre des sources et glossaire de référence |
| [`diagrams/`](diagrams/README.md) | Architecture, parcours PDF, chaîne de confiance et conservation |

## Démarrage et vérification

Suivre le [guide d’installation](docs/fr/installation.md). Les services écoutent sur `127.0.0.1:3000` et `127.0.0.1:8000`. Utiliser des documents fictifs sur un poste individuel.

Les contrôles du projet se lancent avec `python3 scripts/check.py` après installation des dépendances de développement. Le [rapport d’audit](docs/audit.md) décrit les corrections et les limites de la revue.

Le code et la documentation d’origine sont sous [licence MIT](LICENSE). Les publications officielles et les dépendances conservent leurs propres droits : voir les [mentions tierces](THIRD_PARTY_NOTICES.md).

English: local PDF signing and verification with test identities; see the [English handbook](docs/en/README.md).

العربية: تطبيق محلي لتوقيع ملفات PDF والتحقق منها باستخدام هويات اختبار؛ راجع [الدليل العربي](docs/ar/README.md).
