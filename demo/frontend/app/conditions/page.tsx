import AppShell from "../components/app-shell";

export default function TermsPage() {
  return (
    <AppShell section="legal">
      <article className="prose">
        <span className="overline">CADRE D’UTILISATION</span>
        <h1>Conditions d’utilisation</h1>
        <p className="edition">Version du 13 novembre 2026 · Démonstration locale</p>
        <p className="lead">
          DZ Sign est un outil pédagogique du projet DZ Digital Trust. Il permet d’expérimenter la
          signature et la vérification cryptographiques de documents PDF.
        </p>
        <h2>Usage prévu</h2>
        <p>
          Utilisez cette version sur votre poste, avec des documents fictifs et des clés de test.
          Elle ne fournit pas un service de confiance accrédité, une vérification officielle
          d’identité ou une signature qualifiée. Une copie signée avec l’identité fictive ne doit
          pas être présentée comme un acte signé par une personne réelle.
        </p>
        <h2>Actions effectuées</h2>
        <p>
          L’import transmet le fichier à l’API locale. L’action de signature demande une
          confirmation explicite avant de créer une copie avec l’identité de démonstration
          configurée. L’original reste distinct. La vérification fournit un rapport limité aux
          contrôles effectivement réalisés.
        </p>
        <h2>Interprétation des résultats</h2>
        <p>
          Les résultats doivent être lus avec la date d’évaluation, l’ancre de confiance et les
          limites affichées. La révocation, l’horodatage de confiance, la validité historique et la
          qualification juridique ne sont pas établis par cette version. Un résultat indéterminé ne
          doit pas être transformé en conclusion favorable ou défavorable.
        </p>
        <h2>Documents temporaires</h2>
        <p>
          Le service ne constitue pas un espace d’archivage. Les documents expirent après quinze
          minutes au maximum et ne sont pas récupérables après le redémarrage du backend.
          Téléchargez les résultats d’exercice que vous souhaitez garder. Les modalités de
          conservation sont détaillées dans la page de confidentialité.
        </p>
        <h2>Exploitation et évolution</h2>
        <p>
          Le logiciel reste expérimental. Vérifiez ses résultats avant tout usage extérieur à
          l’exercice et ne l’utilisez pas comme unique fondement d’une décision administrative ou
          contractuelle. Un déploiement partagé ou public sort du périmètre local décrit ici. Les
          droits sur le code et la documentation sont définis par le fichier de licence du dépôt.
        </p>
      </article>
    </AppShell>
  );
}
