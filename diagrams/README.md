# Diagrammes du projet

Ces schémas décrivent le fonctionnement actuel de DZ Sign. Les blocs Mermaid sont affichés directement par GitHub ; leur source reste modifiable dans les fichiers Markdown. Ils ne nécessitent aucun service supplémentaire pour l’application.

| Schéma | Ce qu’il explique |
|---|---|
| [Architecture locale](architecture.md) | Interface, API, processus PDF et stockage privé |
| [Signature et vérification](signature.md) | Import, confirmation, copie signée et rapport séparé |
| [Chaîne de confiance](pki.md) | Certificats de test, clé privée et racine explicitement approuvée |
| [Cycle de vie des documents](document-lifecycle.md) | Conservation, expiration et suppression |

Les flèches représentent des échanges ou des relations précis, pas une infrastructure de production. Aucun compte utilisateur, service de révocation ou service d’horodatage n’est représenté comme implémenté.

English: these diagrams document the implemented local architecture, PDF signing and verification, test certificate chain, and temporary document lifecycle. GitHub renders the Mermaid blocks directly.

العربية: توضح هذه المخططات البنية المحلية الحالية، وتوقيع ملفات PDF والتحقق منها، وسلسلة شهادات الاختبار، ودورة الاحتفاظ المؤقت بالوثائق. يعرض GitHub مخططات Mermaid مباشرة.

Pour les paramètres et les commandes, consulter les [manuels](../docs/README.md).
