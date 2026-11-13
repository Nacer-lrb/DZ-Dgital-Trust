# Signature électronique et signature cryptographique

Une signature électronique associe un acte de signature à des données électroniques. Dans DZ Sign, le mécanisme étudié est une signature cryptographique de PDF : une clé privée produit la signature et la clé publique correspondante permet de la vérifier.

L’image d’une signature manuscrite peut être visible dans un PDF sans qu’aucune signature cryptographique soit présente. Inversement, une signature cryptographique peut être invisible à l’écran. Le vérificateur recherche les structures de signature, pas leur apparence graphique.

## Ce que le contrôle distingue

L’intégrité concerne les données couvertes par la signature. La confiance concerne le certificat, sa chaîne et les règles du vérificateur. La période de validité concerne la date d’évaluation. Ces résultats sont séparés dans le rapport ; une réussite de l’un ne remplace pas les autres.

La [fiche de vérification](../cryptography/signature-validation.md) détaille le hachage, les attributs signés, l’horodatage et la révocation. La [présentation de la PKI](../cryptography/pki.md) explique les clés et certificats.

## Périmètre de DZ Sign

L’application signe une copie avec une identité fictive et conserve l’original. Elle n’établit ni une qualification juridique ni une identité réelle. Les notions légales se lisent dans les textes officiels référencés dans le [cadre juridique](../algeria/legal-framework.md).
