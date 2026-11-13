import Link from "next/link";

export default function AppShell({
  children,
  section = "documents",
}: {
  children: React.ReactNode;
  section?: "documents" | "methode" | "legal";
}) {
  return (
    <div className="application">
      <a className="skip-link" href="#main">
        Aller au contenu
      </a>
      <aside className="rail">
        <Link href="/" className="wordmark" aria-label="DZ Sign, documents">
          <span>DZ</span>
          <span>
            SIGN<small>CONFIANCE NUMÉRIQUE</small>
          </span>
        </Link>
        <div className="rail-section">ESPACE DE TRAVAIL</div>
        <nav aria-label="Navigation principale">
          <Link href="/" aria-current={section === "documents" ? "page" : undefined}>
            Documents
          </Link>
          <Link href="/methode" aria-current={section === "methode" ? "page" : undefined}>
            Lire une vérification
          </Link>
        </nav>
        <div className="rail-foot">
          <span className="rail-label">DÉMONSTRATION LOCALE</span>
          <p>
            Des documents fictifs.
            <br />
            Des contrôles explicites.
          </p>
          <span className="rail-edition">DZ DIGITAL TRUST · 2026</span>
        </div>
      </aside>
      <div className="application-body">
        <header className="application-header">
          <span>Documents & services de confiance</span>
          <span className="environment">ENVIRONNEMENT DE TEST</span>
        </header>
        <main id="main">{children}</main>
        <footer className="application-footer">
          <span>Certificats de test uniquement. Aucune qualification juridique établie.</span>
          <div>
            <Link href="/confidentialite">Confidentialité</Link>
            <Link href="/conditions">Conditions d’utilisation</Link>
          </div>
        </footer>
      </div>
    </div>
  );
}
