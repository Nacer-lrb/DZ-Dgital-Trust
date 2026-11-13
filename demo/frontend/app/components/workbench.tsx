"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  API,
  ApiError,
  DocumentInfo,
  getDocuments,
  getHealth,
  Health,
  removeDocument,
  signDocument,
  size,
  uploadDocument,
  Verification,
  verifyDocument,
} from "../lib/api";
import VerificationReport from "./verification-report";

type Operation = "upload" | "sign" | "verify" | "delete" | null;

export default function Workbench() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [connectionError, setConnectionError] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState<Operation>(null);
  const [source, setSource] = useState<"original" | "signed">("original");
  const [report, setReport] = useState<Verification | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [consent, setConsent] = useState(false);
  const [now, setNow] = useState(0);
  const fileInput = useRef<HTMLInputElement>(null);
  const consentInput = useRef<HTMLInputElement>(null);
  const generation = useRef(0);
  const selected = documents.find((document) => document.id === selectedId) ?? null;
  const expired = Boolean(selected && now > 0 && Date.parse(selected.expires_at) <= now);
  const remaining = selected
    ? Math.max(0, Math.ceil((Date.parse(selected.expires_at) - now) / 1000))
    : 0;
  const ready = health !== null && busy === null && !expired;

  const refresh = useCallback(async (signal?: AbortSignal) => {
    const version = ++generation.current;
    setRefreshing(true);
    try {
      const [status, list] = await Promise.all([getHealth(signal), getDocuments(signal)]);
      if (signal?.aborted || version !== generation.current) return;
      setHealth(status);
      setDocuments(list);
      setConnectionError("");
      setSelectedId((current) =>
        list.some((item) => item.id === current) ? current : (list[0]?.id ?? null),
      );
    } catch (cause) {
      if (!signal?.aborted && version === generation.current) {
        setHealth(null);
        setConnectionError(cause instanceof Error ? cause.message : "Connexion impossible.");
      }
    } finally {
      if (!signal?.aborted && version === generation.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void refresh(controller.signal);
    setNow(Date.now());
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      controller.abort();
      clearInterval(timer);
    };
  }, [refresh]);
  useEffect(() => {
    setConfirming(false);
    setConsent(false);
    setSource("original");
    setError("");
  }, [selectedId]);
  useEffect(() => {
    if (confirming) consentInput.current?.focus();
  }, [confirming]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy || !health?.capabilities.upload) return;
    setError("");
    setNotice("");
    if (file.size === 0) {
      setError("Ce fichier est vide. Choisissez un PDF contenant des pages.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("Le PDF doit faire au maximum 10 Mio.");
      return;
    }
    setBusy("upload");
    try {
      const document = await uploadDocument(file);
      setDocuments((current) => [document, ...current]);
      setSelectedId(document.id);
      setFile(null);
      if (fileInput.current) fileInput.current.value = "";
      setNotice(
        "Document importé. Vous pouvez consulter ses informations et choisir un traitement.",
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Import impossible.");
    } finally {
      setBusy(null);
    }
  }

  async function remove() {
    if (!selected || busy) return;
    setBusy("delete");
    setError("");
    setNotice("");
    const id = selected.id;
    try {
      try {
        await removeDocument(id);
      } catch (cause) {
        if (!(cause instanceof ApiError) || ![404, 410].includes(cause.status)) throw cause;
      }
      setDocuments((current) => current.filter((document) => document.id !== id));
      setSelectedId(null);
      if (report?.document_id === id) setReport(null);
      setNotice("Le document et ses résultats ne sont plus conservés dans cet espace.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Suppression impossible.");
    } finally {
      setBusy(null);
    }
  }

  async function sign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || !consent || !ready || !health?.capabilities.sign) return;
    setBusy("sign");
    setError("");
    setNotice("");
    try {
      const result = await signDocument(selected.id);
      setDocuments((current) =>
        current.map((document) =>
          document.id === selected.id ? { ...document, signed_result: result } : document,
        ),
      );
      setSource("signed");
      setReport(null);
      setConfirming(false);
      setConsent(false);
      setNotice("La copie signée est disponible. Le document original a été conservé.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Signature impossible.");
    } finally {
      setBusy(null);
    }
  }

  async function verify() {
    if (!selected || !ready || !health?.capabilities.verify) return;
    setBusy("verify");
    setError("");
    setNotice("");
    setReport(null);
    try {
      setReport(await verifyDocument(selected.id, source));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Vérification impossible.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <div className="page-title">
        <div>
          <span className="overline">REGISTRE TEMPORAIRE</span>
          <h1>Documents</h1>
          <p>Importer, signer une copie de test et examiner ses signatures.</p>
        </div>
        <div className="connection">
          <span>
            {refreshing
              ? "Connexion en cours"
              : health
                ? "Service local connecté"
                : "Service local indisponible"}
          </span>
          <button
            className="button text"
            disabled={refreshing || busy !== null}
            onClick={() => void refresh()}
          >
            Actualiser
          </button>
        </div>
      </div>
      {connectionError && (
        <div className="message error" role="alert">
          <strong>Connexion à rétablir.</strong> {connectionError}{" "}
          <Link href="/methode#demarrage">Aide au démarrage</Link>
        </div>
      )}
      {error && (
        <div className="message error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="message notice" role="status">
          {notice}
        </div>
      )}

      <form className="import-bar" onSubmit={upload}>
        <div className="import-heading">
          <label htmlFor="pdf-file">Ajouter un document</label>
          <span>PDF fictif · 10 Mio maximum · conservation de 15 minutes</span>
        </div>
        <div className="import-controls">
          <input
            ref={fileInput}
            id="pdf-file"
            type="file"
            accept=".pdf,application/pdf"
            disabled={busy !== null}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setError("");
            }}
          />
          <button
            className="button primary"
            type="submit"
            disabled={!file || !health?.capabilities.upload || busy !== null}
          >
            {busy === "upload" ? "Analyse en cours…" : "Importer le PDF"}
          </button>
        </div>
        {busy === "upload" && (
          <div className="operation-progress" role="status">
            <progress aria-label="Import du PDF en cours" />
            <span>Réception et contrôle du PDF. Jusqu’à 30 secondes.</span>
          </div>
        )}
      </form>

      <div className="workbench-grid">
        <div className="document-column">
          <section className="document-register" aria-labelledby="register-title">
            <div className="section-heading">
              <h2 id="register-title">Documents disponibles</h2>
              <span className="count">{documents.length} / 10</span>
            </div>
            {loading ? (
              <div className="loading-state" aria-busy="true" role="status">
                <span>Chargement du registre…</span>
                <div className="skeleton-line" />
                <div className="skeleton-line short" />
                <div className="skeleton-line" />
              </div>
            ) : documents.length === 0 ? (
              <div className="empty-register">
                <h3>
                  {health ? "Aucun document pour le moment." : "Le registre n’est pas disponible."}
                </h3>
                <p>
                  {health
                    ? "Choisissez un PDF fictif ci-dessus. Ses informations apparaîtront ici après contrôle du fichier."
                    : "Démarrez le service local, puis actualisez la connexion pour accéder aux documents."}
                </p>
              </div>
            ) : (
              <div className="table-scroll">
                <table className="document-table">
                  <caption className="sr-only">
                    Documents importés, sélectionnez un nom pour afficher les traitements
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Document</th>
                      <th scope="col">Pages</th>
                      <th scope="col">Taille</th>
                      <th scope="col">État</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((document) => (
                      <tr
                        key={document.id}
                        className={selectedId === document.id ? "is-selected" : ""}
                      >
                        <td>
                          <button
                            className="document-name"
                            aria-pressed={selectedId === document.id}
                            onClick={() => setSelectedId(document.id)}
                            disabled={busy !== null}
                          >
                            {document.name}
                          </button>
                          <small>PDF · {document.id.slice(0, 8)}</small>
                        </td>
                        <td>{document.page_count}</td>
                        <td className="number-cell">{size(document.size_bytes)}</td>
                        <td>
                          <span className="document-state">
                            {now > 0 && Date.parse(document.expires_at) <= now
                              ? "Expiré"
                              : document.signed_result
                                ? "Copie signée"
                                : "Importé"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="register-footnote">
              L’import contrôle la lisibilité du PDF. Il ne valide pas ses signatures.
            </div>
          </section>

          {busy === "verify" && (
            <section className="report-loading" role="status" aria-busy="true">
              <span className="overline">VÉRIFICATION</span>
              <h2>Lecture des signatures…</h2>
              <progress aria-label="Vérification en cours" />
              <p>Le fichier reste sur cette machine. Aucun résultat n’est encore établi.</p>
            </section>
          )}
          {report && selected?.id === report.document_id && <VerificationReport report={report} />}
        </div>

        <aside className="inspector" aria-labelledby="inspector-title">
          <div className="inspector-heading">
            <span className="overline">DOCUMENT SÉLECTIONNÉ</span>
            <h2 id="inspector-title">{selected ? selected.name : "Aucune sélection"}</h2>
          </div>
          {!selected ? (
            <p className="inspector-empty">
              Sélectionnez un document du registre pour consulter ses informations, le signer ou le
              vérifier.
            </p>
          ) : (
            <>
              <dl className="document-facts">
                <div>
                  <dt>Pages</dt>
                  <dd>{selected.page_count}</dd>
                </div>
                <div>
                  <dt>Original</dt>
                  <dd>{size(selected.size_bytes)}</dd>
                </div>
                <div>
                  <dt>Conservation restante</dt>
                  <dd>
                    {expired
                      ? "Document expiré"
                      : `${Math.floor(remaining / 60)} min ${String(remaining % 60).padStart(2, "0")} s`}
                  </dd>
                </div>
              </dl>
              <details className="fingerprint">
                <summary>Empreinte SHA-256 de l’original</summary>
                <code>{selected.sha256}</code>
              </details>
              <div className="original-actions">
                {!expired && (
                  <a href={`${API}/api/documents/${selected.id}/download`}>
                    Télécharger l’original
                  </a>
                )}
                <button
                  className="button text danger"
                  disabled={busy !== null}
                  onClick={() => void remove()}
                >
                  {busy === "delete" ? "Suppression…" : "Supprimer"}
                </button>
              </div>
              {expired && (
                <p className="inline-note">
                  L’échéance est atteinte. Importez le document à nouveau pour poursuivre.
                </p>
              )}

              <section className="treatment">
                <span className="overline">SIGNATURE DE TEST</span>
                <h3>Créer une copie signée</h3>
                <p>
                  L’original est conservé. La copie utilise une identité fictive réservée à la
                  démonstration.
                </p>
                {selected.signed_result ? (
                  <div className="signed-copy">
                    <strong>Copie signée disponible</strong>
                    {selected.signed_result.normalized_before_signing && (
                      <p className="inline-note">
                        La structure hybride du PDF a été réenregistrée avant signature de la copie.
                        L’original reste intact.
                      </p>
                    )}
                    <span>{size(selected.signed_result.size_bytes)}</span>
                    {!expired && (
                      <a
                        className="button secondary"
                        href={`${API}/api/results/${selected.signed_result.id}/download`}
                      >
                        Télécharger la copie signée
                      </a>
                    )}
                    <details className="fingerprint">
                      <summary>Empreinte de la copie</summary>
                      <code>{selected.signed_result.sha256}</code>
                    </details>
                  </div>
                ) : confirming ? (
                  <form className="sign-confirmation" onSubmit={sign}>
                    <label>
                      <input
                        ref={consentInput}
                        type="checkbox"
                        required
                        checked={consent}
                        onChange={(event) => setConsent(event.target.checked)}
                        disabled={busy !== null}
                      />
                      <span>
                        Je souhaite signer ce PDF avec une identité fictive de démonstration.
                      </span>
                    </label>
                    <div>
                      <button className="button primary" disabled={!consent || !ready}>
                        {busy === "sign" ? "Signature en cours…" : "Confirmer la signature de test"}
                      </button>
                      <button
                        className="button text"
                        type="button"
                        disabled={busy !== null}
                        onClick={() => {
                          setConfirming(false);
                          setConsent(false);
                        }}
                      >
                        Annuler
                      </button>
                    </div>
                    {busy === "sign" && <progress aria-label="Signature en cours" />}
                  </form>
                ) : (
                  <>
                    <button
                      className="button secondary"
                      disabled={!ready || !health?.capabilities.sign}
                      onClick={() => setConfirming(true)}
                    >
                      Signer une copie de test
                    </button>
                    {!health?.capabilities.sign && (
                      <p className="inline-note">
                        L’identité de test n’est pas activée sur ce poste.{" "}
                        <Link href="/methode#demarrage">Consulter le guide</Link>
                      </p>
                    )}
                  </>
                )}
              </section>

              <section className="treatment">
                <span className="overline">VÉRIFICATION</span>
                <h3>Examiner les signatures</h3>
                <label className="field-label" htmlFor="verification-source">
                  Version à analyser
                </label>
                <select
                  id="verification-source"
                  value={source}
                  onChange={(event) => setSource(event.target.value as "original" | "signed")}
                  disabled={busy !== null}
                >
                  <option value="original">Document original</option>
                  {selected.signed_result && <option value="signed">Copie signée de test</option>}
                </select>
                <button
                  className="button primary"
                  disabled={!ready || !health?.capabilities.verify}
                  onClick={() => void verify()}
                >
                  {busy === "verify" ? "Vérification en cours…" : "Vérifier les signatures"}
                </button>
                <p className="inline-note">
                  Le rapport distingue les contrôles réussis, les échecs et les points non vérifiés.
                </p>
              </section>
            </>
          )}
        </aside>
      </div>
    </>
  );
}
