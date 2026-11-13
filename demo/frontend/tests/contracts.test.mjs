import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const directory = mkdtempSync(join(tmpdir(), "dz-contracts-"));
let contracts;
try {
  execFileSync(fileURLToPath(new URL("../node_modules/.bin/tsc", import.meta.url)), [
    "--ignoreConfig",
    "--target",
    "ES2022",
    "--module",
    "commonjs",
    "--skipLibCheck",
    "--outDir",
    directory,
    fileURLToPath(new URL("../app/lib/contracts.ts", import.meta.url)),
  ]);
  contracts = createRequire(import.meta.url)(join(directory, "contracts.js"));
} finally {
  rmSync(directory, { recursive: true, force: true });
}
const id = "a".repeat(32);
const sha256 = "b".repeat(64);
const created = "2026-11-13T12:00:00+00:00";
const expires = "2026-11-13T12:15:00+00:00";
const document = {
  id,
  name: "test.pdf",
  sha256,
  size_bytes: 100,
  page_count: 1,
  created_at: created,
  expires_at: expires,
  signed_result: null,
};
const signature = {
  field: "Signature1",
  subject: "TEST",
  issuer: "TEST CA",
  serial_number: "1",
  integrity: "passed",
  cms_signature: "passed",
  certificate_validation: "passed_local_policy",
  coverage: "ENTIRE_FILE",
  modification_level: "NONE",
  pdf_permissions_ok: true,
  outcome: "checks_passed_with_limits",
  certificate_period: { not_before: created, not_after: expires, at_evaluation: "within_period" },
  revocation: "not_verified",
  timestamp: "not_verified",
};
const report = {
  schema_version: 1,
  document_id: id,
  source: "original",
  evaluated_at: created,
  file_sha256: sha256,
  trust_root_sha256: null,
  outcome: "checks_passed_with_limits",
  signatures: [signature],
  legal_qualification: "not_assessed",
  network_fetching: false,
};

test("health requires a positive status and actual boolean capabilities", () => {
  const health = {
    status: "ok",
    service: "dz-sign",
    capabilities: { upload: true, sign: false, verify: true },
  };
  assert.equal(contracts.isHealth(health), true);
  assert.equal(contracts.isHealth({ ...health, status: "failed" }), false);
  assert.equal(contracts.isHealth({ ...health, capabilities: { upload: "true" } }), false);
});
test("documents reject invalid sizes, hashes and dates", () => {
  assert.equal(contracts.isDocument(document), true);
  for (const patch of [
    { size_bytes: -1 },
    { page_count: 1.5 },
    { sha256: "bad" },
    { created_at: "unknown" },
  ]) {
    assert.equal(contracts.isDocument({ ...document, ...patch }), false);
  }
});
test("a signed result must belong to its document", () => {
  const result = {
    id: "c".repeat(32),
    document_id: id,
    name: "signed.pdf",
    sha256,
    size_bytes: 200,
    created_at: created,
    expires_at: expires,
  };
  assert.equal(contracts.isDocument({ ...document, signed_result: result }), true);
  assert.equal(
    contracts.isDocument({
      ...document,
      signed_result: { ...result, document_id: "d".repeat(32) },
    }),
    false,
  );
});
test("incomplete reports are rejected instead of shown as a successful check", () => {
  assert.equal(contracts.isVerification(report), true);
  assert.equal(
    contracts.isVerification({ ...report, signatures: [{ ...signature, certificate_period: {} }] }),
    false,
  );
  assert.equal(contracts.isVerification({ ...report, outcome: "success" }), false);
  assert.equal(contracts.isVerification({ ...report, signatures: [] }), false);
  assert.equal(contracts.isVerification({ ...report, legal_qualification: "qualified" }), false);
});
test("the contract preserves known verification limits", () => {
  assert.equal(
    contracts.isVerification({ ...report, signatures: [{ ...signature, revocation: "verified" }] }),
    false,
  );
  assert.equal(contracts.isVerification({ ...report, network_fetching: true }), false);
  assert.equal(
    contracts.isVerification({ ...report, outcome: "no_signature", signatures: [] }),
    true,
  );
});
