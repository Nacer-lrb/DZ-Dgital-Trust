# PAdES, CAdES et XAdES : choisir un format de signature

Une signature doit être stockée et reliée aux données qu’elle protège. Le format détermine comment les applications retrouvent ces éléments et les interprètent. Cette fiche compare trois familles documentées par l’ETSI, puis précise le choix de DZ Sign.

Consultation des sources : **11 novembre 2026**. Les versions ci-dessous sont les éditions utilisées pour cette documentation ; leur présence dans le registre ne constitue pas une déclaration de conformité.

## Trois familles, trois supports

| Famille | Base technique | Exemple pédagogique proposé |
|---|---|---|
| PAdES | Signature intégrée à un document PDF | Télécharger une attestation PDF signée et l’ouvrir dans un lecteur compatible |
| CAdES | Signature fondée sur CMS | Vérifier un fichier de données accompagné de sa signature détachée |
| XAdES | Signature XML enrichie de propriétés de qualification | Vérifier les éléments référencés d’un document XML métier |

Références officielles : [PAdES, EN 319 142-1 V1.2.1](https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf), [CAdES, EN 319 122-1 V1.3.1](https://www.etsi.org/deliver/etsi_en/319100_319199/31912201/01.03.01_60/en_31912201v010301p.pdf) et [XAdES, EN 319 132-1 V1.2.1](https://www.etsi.org/deliver/etsi_en/319100_319199/31913201/01.02.01_60/en_31913201v010201p.pdf).

### CAdES : travailler avec des données de formats variés

CAdES s’appuie sur les structures CMS et leurs attributs. Le contenu peut être encapsulé ou fourni séparément. Dans le second cas, le vérificateur a besoin du contenu exact auquel la signature se rapporte : changer ses octets change ce qui est vérifié. Voir l’[EN 319 122-1, sections 4 à 6](https://www.etsi.org/deliver/etsi_en/319100_319199/31912201/01.03.01_60/en_31912201v010301p.pdf).

Pour un futur exemple DZ Digital Trust, nous pourrions fournir un fichier et une signature détachée avec des instructions identifiant les deux éléments. Cette possibilité reste hors du premier parcours de l’application.

### XAdES : comprendre les références XML

XAdES ajoute des propriétés à XML Signature, notamment pour identifier le certificat et porter des preuves de validation. Voir l’[EN 319 132-1, sections 4 à 6](https://www.etsi.org/deliver/etsi_en/319100_319199/31913201/01.02.01_60/en_31913201v010201p.pdf).

XML Signature utilise des références, des transformations et une canonicalisation. La vérification doit déterminer précisément quels objets sont signés ; une signature valide ne signifie pas que chaque élément affiché par l’application est couvert. Voir [XML Signature 1.1, sections 3 et 4](https://www.w3.org/TR/xmldsig-core1/).

Un exemple futur devra montrer les éléments réellement référencés, sans effectuer de récupération arbitraire de ressources externes. Aucun moteur XML de signature n’est ajouté à DZ Sign à cette étape.

## Comprendre les niveaux baseline

Les trois familles définissent des niveaux B-B, B-T, B-LT et B-LTA. Ils organisent l’ajout de preuves temporelles et d’éléments utiles à la validation prolongée ; les exigences précises dépendent du format. Consulter les sections 6 des trois normes citées.

Ces désignations techniques ne décident pas à elles seules de la qualification juridique d’une signature. Dans le projet, nous conserverons des champs distincts pour le profil identifié, les contrôles effectués et leurs résultats.

## Décision pour DZ Sign

Le premier parcours concerne un document PDF : nous retenons donc PAdES comme objectif d’implémentation. La [fiche PAdES](pades.md) précise le niveau visé, les limites et les vérifications à préparer. CAdES et XAdES restent documentés pour situer ce choix ; leur prise en charge n’est pas annoncée dans la première version.
