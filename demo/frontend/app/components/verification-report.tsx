import { useEffect, useRef } from "react";
import { time, Verification } from "../lib/api";

const outcomes: Record<string, [string, string]> = {
  checks_passed_with_limits: [
    "Les contrôles locaux ont réussi.",
    "L’intégrité et le certificat ont été contrôlés selon la configuration de test. Des vérifications restent hors périmètre.",
  ],
  checks_failed: [
    "Certains contrôles ne sont pas satisfaits.",
    "Consultez les résultats séparés ci-dessous. Un problème de confiance du certificat ne signifie pas nécessairement que le fichier a été modifié.",
  ],
  no_signature: [
    "Aucune signature cryptographique détectée.",
    "Une image de signature ou de cachet ne constitue pas, à elle seule, une signature cryptographique.",
  ],
  needs_review: [
    "Les révisions du document demandent un examen.",
    "Une signature peut rester correcte sur une ancienne révision sans couvrir tout le fichier actuel.",
  ],
  indeterminate: [
    "La vérification ne permet pas de conclure.",
    "Une analyse impossible ne prouve pas que la signature est incorrecte.",
  ],
};
const checks: Record<string, string> = {
  passed: "Vérifiée",
  failed: "Échec",
  indeterminate: "Indéterminée",
  passed_local_policy: "Approuvé dans la configuration de test",
  not_established: "Confiance non établie",
  within_period: "Dans la période de validité",
  outside_period: "Hors période de validité",
  ENTIRE_FILE: "Fichier entier",
  ENTIRE_REVISION: "Révision signée uniquement",
  CONTIGUOUS_BLOCK_FROM_START: "Couverture partielle",
  UNCLEAR: "À examiner",
  not_verified: "Non vérifié",
};
function label(value: string) {
  return checks[value] ?? "À examiner";
}

export default function VerificationReport({ report }: { report: Verification }) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
  }, [report]);
  const [title, description] = outcomes[report.outcome] ?? outcomes.indeterminate;
  function download() {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = "verification-dz-sign.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return (
    <section className="report" aria-labelledby="report-title">
      <div className="section-heading">
        <div>
          <span className="overline">RAPPORT DE VÉRIFICATION</span>
          <h2 ref={heading} tabIndex={-1} id="report-title">
            {report.source === "signed" ? "Copie signée" : "Document original"}
          </h2>
        </div>
        <button className="button text" onClick={download}>
          Exporter le rapport JSON
        </button>
      </div>
      <div
        className={`report-conclusion ${report.outcome === "checks_passed_with_limits" ? "favorable" : "attention"}`}
        role="status"
      >
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      <div className="report-date">
        Évalué le {time(report.evaluated_at)} UTC · {report.signatures.length} signature
        {report.signatures.length > 1 ? "s" : ""} détectée{report.signatures.length > 1 ? "s" : ""}
      </div>
      {report.signatures.map((signature, index) => (
        <article className="signature-result" key={`${signature.field}-${index}`}>
          <div className="signature-heading">
            <h3>Signature {String(index + 1).padStart(2, "0")}</h3>
            <span>{signature.field}</span>
          </div>
          <dl className="certificate-identity">
            <div>
              <dt>Sujet du certificat</dt>
              <dd>{signature.subject}</dd>
            </div>
            <div>
              <dt>Émetteur</dt>
              <dd>{signature.issuer}</dd>
            </div>
          </dl>
          <table className="checks-table">
            <caption className="sr-only">Contrôles de la signature {index + 1}</caption>
            <tbody>
              <tr>
                <th scope="row">Intégrité des données couvertes</th>
                <td className={signature.integrity === "failed" ? "negative" : ""}>
                  {label(signature.integrity)}
                </td>
              </tr>
              <tr>
                <th scope="row">Signature cryptographique</th>
                <td>{label(signature.cms_signature)}</td>
              </tr>
              <tr>
                <th scope="row">Confiance du certificat</th>
                <td>{label(signature.certificate_validation)}</td>
              </tr>
              <tr>
                <th scope="row">Période de validité</th>
                <td>
                  {label(signature.certificate_period.at_evaluation)}
                  <small>
                    {time(signature.certificate_period.not_before)} au{" "}
                    {time(signature.certificate_period.not_after)} UTC
                  </small>
                </td>
              </tr>
              <tr>
                <th scope="row">Couverture du document</th>
                <td>{label(signature.coverage)}</td>
              </tr>
              <tr>
                <th scope="row">Révocation</th>
                <td>Non vérifiée</td>
              </tr>
              <tr>
                <th scope="row">Horodatage de confiance</th>
                <td>Non vérifié</td>
              </tr>
            </tbody>
          </table>
          {signature.error && (
            <details className="technical-detail">
              <summary>Détail du contrôle interrompu</summary>
              <p>{signature.error}</p>
            </details>
          )}
        </article>
      ))}
      <div className="report-limits">
        <strong>Portée de ce rapport</strong>
        <p>
          Vérification locale, à la date indiquée. La révocation, la preuve d’horodatage, la
          qualification juridique et la validation historique ne sont pas établies.
        </p>
        <details>
          <summary>Empreinte et ancre de confiance utilisées</summary>
          <dl>
            <dt>SHA-256 du fichier analysé</dt>
            <dd>
              <code>{report.file_sha256}</code>
            </dd>
            <dt>Ancre explicitement approuvée</dt>
            <dd>
              <code>{report.trust_root_sha256 ?? "Aucune ancre configurée"}</code>
            </dd>
          </dl>
        </details>
      </div>
    </section>
  );
}
