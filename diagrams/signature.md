# Import, signature et vérification

La signature produit une copie. La vérification est une action séparée : la disponibilité d’un téléchargement ne constitue pas un verdict sur sa signature.

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant B as Interface
    participant A as API locale
    participant W as Processus PDF
    participant D as Stockage temporaire
    U->>B: Choisir un PDF fictif
    B->>A: POST /api/documents (multipart)
    A->>A: Contrôler taille et capacité du registre
    A->>D: Enregistrer l’original et calculer SHA-256
    A->>W: Inspecter le PDF
    W-->>A: Métadonnées ou erreur
    A-->>B: Identifiant, empreinte, échéance
    U->>B: Confirmer la signature de test
    B->>A: POST /api/documents/{id}/sign
    A->>W: Signer avec l’identité configurée
    opt PDF hybride sans signature existante
        W->>W: Réécrire une copie avant signature
    end
    W->>D: Écrire signed.pdf, conserver l’original
    W-->>A: Succès ou erreur
    A->>A: Recontrôler échéance, taille et empreinte du résultat
    A-->>B: Référence de téléchargement et éventuelle normalisation
    U->>B: Vérifier la copie signée
    B->>A: POST /api/documents/{id}/verify, source signed
    A->>W: Vérifier avec la racine configurée
    W-->>A: Rapport structuré
    A-->>B: Rapport après contrôle de l’échéance
    B-->>U: Résultats détaillés et export JSON
```

Tout échec d’import empêche l’enregistrement du document dans le registre. Un échec de signature entraîne la suppression de la sortie partielle. Un original contenant déjà une signature est refusé pour la signature de test ; il peut être vérifié directement.

Le rapport distingue intégrité, certificat et couverture du document. La révocation et l’horodatage de confiance restent non vérifiés. HTTP 200 indique qu’un rapport a été produit, pas que tous les contrôles sont favorables. L’original peut aussi être vérifié en choisissant `source: original`.

Références : [orchestration réelle](../demo/backend/app/documents.py), [signature PDF](../examples/pdf-signing/sign_pdf.py), [vérification PDF](../examples/pdf-signing/verify_pdf.py).
