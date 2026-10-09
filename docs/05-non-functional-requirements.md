# QuantX — Non-Functional Requirements

**Status:** Pre-implementation · **Depends on:** `10-security-requirements.md` (SR register, mandatory tests), `00-index.md` (open decisions)

## Security

- Hybrid-mode-by-default posture: PQC-only and classical-only require explicit server-side opt-in; never negotiable from wire data (D2, SR-1).
- No primitive cryptography is implemented in-house — only orchestration around `cryptography` (D1).
- Mandatory automated security tests, present as soon as the relevant layer is built and never removed: hybrid-downgrade rejection, replay rejection, per-identity and global rate-limit rejection, KEM ciphertext/public-key substitution rejection, wire-parser fuzzing (`10-security-requirements.md`).
- Every `GATE_REVIEW_REQUIRED` component (`SignatureCombiner`, `KEMCombiner`, `AlgorithmRegistry`, `KeyWallet` backends, `ThresholdPolicy`/`ThresholdManager`, `MerkleMembershipProof`, `AnonymousProofBackend`) is withheld from any "production-ready" claim until independently reviewed and logged.
- Any material referencing PQC adapters carries the PQC backend statement (D-006), every time they're mentioned in client-facing material.

## Performance & scalability

- **No hard latency targets exist yet — this is intentionally open (D8).** Real numbers get set from benchmarking once Layers 0–4 exist, not guessed here.
- **Wire-size budget (set now, not deferred):** PQC signatures/ciphertexts are materially larger than classical ones — ML-DSA-65 signatures run roughly 3.3KB versus Ed25519's 64 bytes; ML-KEM-768 ciphertexts run roughly 1.1KB versus X25519's 32 bytes. A hybrid exchange (both combined, plus framing) lands in the ballpark of 4–5KB per auth round-trip. Provisional budget: **under 8KB per exchange**, revisit once real numbers exist. The REST sidecar (`08-api-specification.md`) sends raw binary bodies, not base64-in-JSON, specifically because base64 adds ~33% overhead on payloads already this size.
- Horizontal scalability is proven by the `InMemoryKVStore` → networked-backend swap requiring zero changes to Layers 1–4 (SR-3, SR-4).
- `InMemoryKVStore` enforces a hard `max_entries` cap and is dev/test-only by contract, never a production recommendation (SR-3).

## Availability & resilience

- A networked `KeyValueStore` backend treats connection failure as a first-class case with an explicit decision (fail-closed vs. degrade), not an unhandled exception (SR-4).
- Backend-unavailable states (`HsmPkcs11Backend`, `OSKeychainBackend`) raise explicit, typed errors rather than degrading silently to weaker behavior (SR-6).

## Observability

- Layer 10's compliance/CBOM tooling is deployable independently of the auth engine — a client can run a crypto inventory scan without adopting QuantX for auth at all.
- `TlsInspector` output is tagged by trust level (`"trust": "verified"` vs `"unverified"`) so downstream consumers can filter on evidentiary strength, not just presence (SR-13).
- `StaticSourceScanner` output is never presented without its permanent best-effort disclaimer (SR-15).

## Compliance & standards posture

- No FIPS-validation or formal-review claim is made anywhere until the relevant `GATE_REVIEW_REQUIRED` items are actually cleared — this is a hard rule, not a marketing decision.
- `StandardsCatalog` (NIST FIPS 203/204/205 etc.) is swappable data, not hardcoded into `ComplianceReportGenerator` (FR-10.4), so the standards posture can be updated without touching report-generation logic.

## Maintainability & code quality

- `ruff`, `black`, and `mypy --strict` run in CI on every change.
- Layer-1 adapters stay ~30–60 lines each; anything that grows past that belongs in a different layer (FR-1.3).
- No component above Layer 1 imports a sibling concrete class except `AlgorithmRegistry` (FR-X.2) — enforced by import-linting in CI, not just code review.
- Every module docstring follows the fixed contract order.

## Auditability

- Every item in the security requirements register (`10-security-requirements.md`) has a named enforcement point and a named test; this doc set traces each one so nothing silently regresses.
- `docs/adr/` is where `GATE_REVIEW_REQUIRED` sign-offs get logged — a reviewer should be able to find, for any Layer-2+ component, whether and when it was reviewed.

## Explicitly not addressed by this doc

- Legal entity structure, funding, and solo-vs-team execution (D9) — business decisions, not engineering NFRs.
- Concrete latency SLAs (D8) — deferred to post-benchmark, tracked as an open item rather than invented. The wire-size budget above is set now because the underlying numbers are public and don't require benchmarking to know.
