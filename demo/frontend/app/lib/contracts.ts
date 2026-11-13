export type SignedResult = {
  id: string;
  document_id: string;
  name: string;
  sha256: string;
  size_bytes: number;
  created_at: string;
  expires_at: string;
  normalized_before_signing?: boolean;
};
export type DocumentInfo = {
  id: string;
  name: string;
  sha256: string;
  size_bytes: number;
  page_count: number;
  created_at: string;
  expires_at: string;
  signed_result: SignedResult | null;
};
export type Health = {
  status: "ok";
  service: "dz-sign";
  capabilities: { upload: boolean; sign: boolean; verify: boolean };
};
export type Signature = {
  field: string;
  subject: string;
  issuer: string;
  serial_number: string;
  integrity: string;
  cms_signature: string;
  certificate_validation: string;
  coverage: string;
  modification_level: string;
  pdf_permissions_ok: boolean | null;
  outcome: string;
  certificate_period: { not_before: string; not_after: string; at_evaluation: string };
  revocation: string;
  timestamp: string;
  error?: string;
};
export type Verification = {
  schema_version: 1;
  document_id: string;
  source: "original" | "signed";
  evaluated_at: string;
  file_sha256: string;
  trust_root_sha256: string | null;
  outcome: string;
  signatures: Signature[];
  legal_qualification: "not_assessed";
  network_fetching: false;
};

export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
const identifier = (v: unknown): v is string => typeof v === "string" && /^[a-f0-9]{32}$/.test(v);
const digest = (v: unknown): v is string => typeof v === "string" && /^[a-f0-9]{64}$/.test(v);
const date = (v: unknown): v is string => typeof v === "string" && Number.isFinite(Date.parse(v));
const positiveInteger = (v: unknown): v is number =>
  typeof v === "number" && Number.isSafeInteger(v) && v > 0;
const outcomes = new Set([
  "checks_passed_with_limits",
  "checks_failed",
  "needs_review",
  "indeterminate",
  "no_signature",
]);

export function isSignedResult(v: unknown): v is SignedResult {
  return (
    isObject(v) &&
    identifier(v.id) &&
    identifier(v.document_id) &&
    typeof v.name === "string" &&
    digest(v.sha256) &&
    positiveInteger(v.size_bytes) &&
    date(v.created_at) &&
    date(v.expires_at) &&
    (v.normalized_before_signing === undefined || typeof v.normalized_before_signing === "boolean")
  );
}
export function isDocument(v: unknown): v is DocumentInfo {
  return (
    isObject(v) &&
    identifier(v.id) &&
    typeof v.name === "string" &&
    digest(v.sha256) &&
    positiveInteger(v.size_bytes) &&
    positiveInteger(v.page_count) &&
    date(v.created_at) &&
    date(v.expires_at) &&
    (v.signed_result === null ||
      (isSignedResult(v.signed_result) && v.signed_result.document_id === v.id))
  );
}
export function isHealth(v: unknown): v is Health {
  return (
    isObject(v) &&
    v.status === "ok" &&
    v.service === "dz-sign" &&
    isObject(v.capabilities) &&
    [v.capabilities.upload, v.capabilities.sign, v.capabilities.verify].every(
      (value) => typeof value === "boolean",
    )
  );
}
function isSignature(v: unknown): v is Signature {
  if (!isObject(v) || !isObject(v.certificate_period)) return false;
  const period = v.certificate_period;
  return (
    [
      v.field,
      v.subject,
      v.issuer,
      v.serial_number,
      v.coverage,
      v.modification_level,
      v.certificate_validation,
    ].every((value) => typeof value === "string") &&
    [v.integrity, v.cms_signature].every(
      (value) => typeof value === "string" && ["passed", "failed", "indeterminate"].includes(value),
    ) &&
    typeof v.outcome === "string" &&
    outcomes.has(v.outcome) &&
    date(period.not_before) &&
    date(period.not_after) &&
    ["within_period", "outside_period"].includes(period.at_evaluation as string) &&
    (typeof v.pdf_permissions_ok === "boolean" || v.pdf_permissions_ok === null) &&
    v.revocation === "not_verified" &&
    v.timestamp === "not_verified" &&
    (v.error === undefined || typeof v.error === "string")
  );
}
export function isVerification(v: unknown): v is Verification {
  return (
    isObject(v) &&
    v.schema_version === 1 &&
    identifier(v.document_id) &&
    ["original", "signed"].includes(v.source as string) &&
    date(v.evaluated_at) &&
    digest(v.file_sha256) &&
    (v.trust_root_sha256 === null || digest(v.trust_root_sha256)) &&
    typeof v.outcome === "string" &&
    outcomes.has(v.outcome) &&
    Array.isArray(v.signatures) &&
    v.signatures.every(isSignature) &&
    (v.outcome === "no_signature" ? v.signatures.length === 0 : v.signatures.length > 0) &&
    v.legal_qualification === "not_assessed" &&
    v.network_fetching === false
  );
}
