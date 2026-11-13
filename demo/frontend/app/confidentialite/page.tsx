import AppShell from "../components/app-shell";

export default function PrivacyPage() {
  return (
    <AppShell section="legal">
      <article className="prose">
        <span className="overline">INFORMATIONS SUR LES DONNÉES</span>
        <h1>Confidentialité</h1>
        <p className="edition">Version du 13 novembre 2026 · Démonstration locale</p>
        <p className="lead">
          Cette page décrit le fonctionnement de la version locale fournie avec le projet. Utilisez
          des documents fictifs et des certificats réservés aux essais.
        </p>
        <h2>Documents et métadonnées</h2>
        <p>
          Le PDF est envoyé à l’API locale après votre action d’import. L’original et, si vous la
          créez, sa copie signée sont enregistrés temporairement sur la machine qui exécute le
          backend. Le nom du fichier, sa taille, son nombre de pages, son empreinte et ses échéances
          sont conservés en mémoire du service.
        </p>
        <p>
          Le registre présente les documents de cette instance locale. Il n’existe pas de comptes ou
          de séparation entre plusieurs utilisateurs : cette version est destinée à une seule
          personne sur son poste.
        </p>
        <h2>Conservation et suppression</h2>
        <p>
          L’accès aux documents et à leurs résultats expire au maximum quinze minutes après le début
          de l’import. La consultation, la signature et la vérification ne prolongent pas ce délai.
          Le nettoyage physique intervient chaque minute, à l’arrêt normal et au redémarrage du
          service. Le bouton « Supprimer » retire le document et sa copie conservée par
          l’application.
        </p>
        <p>
          Les fichiers téléchargés restent dans l’emplacement choisi par votre navigateur.
          L’application ne peut pas les effacer. La suppression du stockage temporaire ne garantit
          pas un effacement forensique du support.
        </p>
        <h2>Certificats et secrets de test</h2>
        <p>
          Les clés privées de démonstration restent côté backend. Elles ne sont pas demandées au
          navigateur. Le processus de signature lit le secret local configuré pour déchiffrer la clé
          en mémoire ; il ne le renvoie pas dans les réponses ou les rapports.
        </p>
        <p>
          Les rapports peuvent contenir des informations publiques présentes dans les certificats,
          notamment le sujet, l’émetteur et les dates. Un rapport JSON téléchargé reste lui aussi
          sous votre contrôle.
        </p>
        <h2>Navigateur, réseau et journaux</h2>
        <p>
          Cette interface n’utilise aucun cookie d’analyse, police distante ou outil d’analyse
          d’audience. Le registre est relu depuis l’API ; aucun contenu PDF n’est enregistré dans le
          stockage du navigateur par l’application. La télémétrie du framework est désactivée dans
          les commandes de lancement fournies.
        </p>
        <p>
          Les traitements PDF sont configurés sans récupération automatique de certificats,
          d’informations de révocation ou d’horodatage sur Internet. Les journaux d’accès du serveur
          peuvent contenir l’adresse locale du client, les routes et identifiants demandés et les
          codes HTTP ; ils ne sont pas conçus pour enregistrer le contenu des PDF ou les secrets.
        </p>
        <h2>Limites du mode local</h2>
        <p>
          Les fichiers sont protégés par les permissions du système, mais cette démonstration n’est
          pas un coffre-fort documentaire. Une personne ayant accès au même compte système peut
          accéder au stockage. Toute adaptation à un service partagé ou hébergé demande une nouvelle
          analyse des accès, des données et des règles applicables.
        </p>
      </article>
    </AppShell>
  );
}
