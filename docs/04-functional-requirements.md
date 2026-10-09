# QuantX — Functional Requirements

**Status:** Pre-implementation · **Depends on:** `06-system-architecture.md` for exact interfaces; this doc states *what must be true*, not *how the signature looks*. Organized by build-order layer (`02-build-order.md`) — no phases.

Each requirement is phrased so it's testable. "Acceptance" points to the Definition of Done in `02-build-order.md`.

## Layer 0 — Foundational interfaces

| ID | Requirement |
|---|---|
| FR-0.1 | `Verifier.verify()` never raises. Any internal exception is caught and converted to `False`. |
| FR-0.2 | Every stateful component's persistence goes through `KeyValueStore`. No component may hold its own ad hoc dict/cache for anything that must survive across calls. |
| FR-0.3 | `Clock` is always injected. No component reads wall-clock time directly, and no component uses an `x or default` pattern on a timestamp (SR-14). |
| FR-0.4 | `Canonicalizer.canonicalize()` is the only path by which structured data is turned into bytes before signing, system-wide (SR-8). |

## Layer 1 — Algorithm adapters

| ID | Requirement |
|---|---|
| FR-1.1 | Each adapter implements exactly one algorithm. No adapter contains a branch on `family`. |
| FR-1.2 | Full adapter set ships together, in one pass (D10): Ed25519, ECDSA-P256, ML-DSA-65, ML-DSA-87, X25519, ML-KEM-768, ML-KEM-1024. SLH-DSA is excepted: blocked on upstream support in `cryptography`, and no other library may stand in for it (D-006). |
| FR-1.3 | Each adapter stays ~30–60 lines; if it grows past that, the excess logic belongs in a different layer, not in the adapter. |

## Layer 2 — Combiners

| ID | Requirement |
|---|---|
| FR-2.1 | Exactly one `SignatureCombiner` class exists in the system. Algorithm pairing is constructor-time wiring, never a new class. |
| FR-2.2 | Exactly one `KEMCombiner` class exists, same rule. |
| FR-2.3 | `required_mode` is set at construction time by the server and is never read from wire data to decide acceptance. The wire-declared mode is used only to parse the bytes, then cross-checked against `required_mode` before any cryptographic verification runs; mismatch rejects unconditionally (SR-1). |
| FR-2.4 | `KEMCombiner` binds ciphertext and public key into the HKDF `info` parameter, so a ciphertext/public-key substitution is cryptographically detectable, not just policy-detectable (SR-7). |

## Layer 3 — Registry

| ID | Requirement |
|---|---|
| FR-3.1 | `AlgorithmRegistry` is the single place in the codebase allowed to import every Layer-1 adapter directly. |
| FR-3.2 | Registry roles (e.g. `session-auth`, `session-auth-pqc-only`) map a name to a concrete algorithm pairing + required mode, loaded from YAML. |
| FR-3.3 | Dev/demo config may load unsigned (`allow_unsigned=True`); the signed-config path is built from the start and is what any non-dev deployment (Recipe B/C) uses — it rejects unsigned config. |

## Layer 4 — Session

| ID | Requirement |
|---|---|
| FR-4.1 | `ChallengeIssuer` produces a challenge that is stored via `KeyValueStore`, not held in process memory outside that interface. |
| FR-4.2 | A consumed challenge/token cannot be replayed — `ReplayStore.consume_once` semantics apply to every replay-sensitive flow. |
| FR-4.3 | `SessionOrchestrator` mints a session token only as the last statement after every required gate has passed. No exception path may leave a live token behind (SR-10). |
| FR-4.4 | Both a per-identity and a global `RateLimiter` gate challenge issuance and verification. |

## Layer 5 — Second factor

| ID | Requirement |
|---|---|
| FR-5.1 | `TotpProvider` verifies offline TOTP/HOTP codes and integrates into `SessionOrchestrator` as an additional required gate, not a replacement for the primary factor. |
| FR-5.2 | TOTP verification has its own rate limiter, independent of the Layer 4 session limiter. |
| FR-5.3 | `PushAuthenticator` gates challenge issuance behind a rate limiter before sending a push (SR-5), and consumes approvals through `ReplayStore` so a push approval cannot be replayed (SR-11). |
| FR-5.4 | TOTP/HOTP secret storage is wired through Layer 6's `KeyWallet` as soon as it exists (D11) — no interim `KeyValueStore`-backed secret store is built to be thrown away later. |

## Layer 6–7 — Key custody & recovery

| ID | Requirement |
|---|---|
| FR-6.1 | `KeyWallet` delegates actual storage to a backend implementing a shared interface; the wallet itself contains no storage logic. |
| FR-6.2 | `EncryptedFileBackend` includes vault metadata in the AES-GCM AAD, so metadata tampering is detected, not just payload tampering (SR-9). |
| FR-6.3 | Corruption of vault contents raises an explicit error. It must never silently return an empty result. |
| FR-6.4 | `BackupCodeManager` verifies each code exactly once; a consumed code cannot be reused. |
| FR-6.5 | `OSKeychainBackend` and `HsmPkcs11Backend` are built as real integrations — the HSM backend against SoftHSM2 if no client hardware is available yet — and either work for real or raise `NotImplementedError` / `BackendUnavailableError`. Neither may silently behave like an in-memory dict while claiming otherwise (SR-6). |

## Layer 8 — Governance

| ID | Requirement |
|---|---|
| FR-8.1 | `ThresholdPolicy` rejects duplicate keys at policy-creation time, not at finalize time (SR-12). |
| FR-8.2 | `ThresholdManager.finalize()` only executes the gated action once quorum is met, using the already-verified `SignatureCombiner` underneath — no separate signature-verification logic is reimplemented here. |

## Layer 9 — Membership/anonymity proofs

| ID | Requirement |
|---|---|
| FR-9.1 | `MerkleMembershipProof`'s verifier actually walks the authentication path to the root and checks it — it must not return a fixed/placeholder result (SR-2). |
| FR-9.2 | `AnonymousProofBackend` remains `NotImplementedError` until a specific concrete implementation has passed a funded, scoped external audit. No interim implementation may claim anonymity. This gate is about audit availability, not build order. |
| FR-9.3 | Any surface (doc, UI, pitch material) presenting `MerkleMembershipProof` states plainly that it is sound but non-anonymous — this caveat may not be omitted or buried. |

## Layer 10 — Observability & compliance

| ID | Requirement |
|---|---|
| FR-10.1 | `StaticSourceScanner`'s output states, every time it's produced, that results are best-effort with real false positives/negatives — not just in a README (SR-15). |
| FR-10.2 | `TlsInspector` performs an authenticated probe (real cert/hostname validation) and a separate, explicitly opt-in permissive probe (`CERT_NONE`); every finding from the permissive probe is tagged `"trust": "unverified"` (SR-13). |
| FR-10.3 | `TlsInspector` parses the fetched certificate itself (`cryptography.x509.load_der_x509_certificate`) and reports the leaf cert's own signature algorithm and key size — it does not merely fetch the cert without reading it. |
| FR-10.4 | `ComplianceReportGenerator` contains no scanning logic and no standards data of its own — swapping `StandardsCatalog` requires zero changes here. |

## Cross-cutting (every layer)

| ID | Requirement |
|---|---|
| FR-X.1 | Every component's module docstring follows the fixed contract order (Layer, Depends on, Implements, Outside, Inside, Wire format, Security notes) exactly. |
| FR-X.2 | No component above Layer 1 imports a sibling concrete class, except `AlgorithmRegistry` (FR-3.1). |
| FR-X.3 | Any `GATE_REVIEW_REQUIRED = True` component cannot be described as production-ready anywhere until its checklist item is complete and logged in `docs/adr/`. |
