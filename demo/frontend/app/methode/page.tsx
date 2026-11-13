import Link from "next/link";
import AppShell from "../components/app-shell";

export default function MethodPage() {
  return (
    <AppShell section="methode">
      <article className="prose">
        <span className="overline">GUIDE DE LECTURE</span>
        <h1>Comprendre une vérification</h1>
        <p className="lead">
          Un rapport utile précise ce qui a été contrôlé, à quelle date et avec quelle confiance.
          Ses résultats doivent être lus séparément.
        </p>
        <h2>Intégrité des données</h2>
        <p>
          Le contrôle d’intégrité examine les données couvertes par la signature. Un échec signifie
          que ces données ne correspondent pas à la signature. Une réussite ne suffit pas à établir
          la confiance dans l’identité indiquée par le certificat.
        </p>
        <h2>Certificat et confiance</h2>
        <p>
          La vérification utilise uniquement la racine de test explicitement configurée sur ce
          poste. Un certificat externe peut donc être non approuvé alors que sa signature
          cryptographique est correcte. Le nom du sujet est une information du certificat, pas une
          identité vérifiée par cette application.
        </p>
        <h2>Dates et révisions PDF</h2>
        <p>
          La période de validité est évaluée à la date courante indiquée dans le rapport. Si des
          révisions ont été ajoutées après signature, le rapport les signale : la signature d’une
          ancienne révision ne vaut pas approbation de tout le fichier actuel.
        </p>
        <h2>Points non vérifiés</h2>
        <p>
          Cette version n’établit pas le statut de révocation, la fiabilité d’un horodatage, la
          validité historique ou une qualification juridique. Un résultat favorable conserve ces
          limites. Un rapport « indéterminé » ne doit pas être interprété comme une preuve
          d’altération.
        </p>
        <h2 id="demarrage">Démarrer l’application</h2>
        <p>Depuis la racine du dépôt, démarrez l’API locale dans un terminal :</p>
        <pre>
          <code>{`.local/dz-sign/venv/bin/python -m uvicorn app.main:app \\\n  --app-dir demo/backend --host 127.0.0.1 --port 8000`}</code>
        </pre>
        <p>Dans un second terminal, démarrez l’interface :</p>
        <pre>
          <code>{`cd demo/frontend\nnpm run dev`}</code>
        </pre>
        <p>
          Ouvrez l’adresse <code>http://127.0.0.1:3000</code>. Si les dépendances manquent, suivez
          le fichier <code>demo/README.md</code> du projet.
        </p>
        <h2>Activer l’identité fictive de signature</h2>
        <p>
          La vérification ne nécessite aucune clé privée. Pour signer une copie de démonstration,
          préparez une identité locale une seule fois :
        </p>
        <pre>
          <code>.local/dz-sign/venv/bin/python demo/backend/setup_demo.py</code>
        </pre>
        <p>
          Ce script génère des clés et des secrets privés hors du suivi Git. Il refuse d’écraser une
          identité existante. Actualisez ensuite la connexion dans l’application. Il ne crée pas un
          certificat qualifié et ne vérifie aucune identité réelle.
        </p>
        <p>
          <Link href="/">Retour aux documents</Link>
        </p>
      </article>
    </AppShell>
  );
}
