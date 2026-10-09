# QuantX — Security Requirements

**Status:** Pre-implementation · This is the authoritative security requirements register for QuantX. Every item below is a first-party design requirement, established before any code exists — not a fix to a prior finding, because there is no prior codebase.

## Foundational rules

- No primitive cryptography implemented in-house — orchestration and composition only, over `cryptography` (D1).
- Hybrid-by-default; PQC-only/classical-only are explicit server-side opt-ins, never client-negotiated (D2).
- All state through `KeyValueStore` — no component-local caches that bypass replay/rate-limit enforcement.
- `Clock` always injected — no direct wall-clock reads.
- Nothing is called "production-ready" anywhere for a `GATE_REVIEW_REQUIRED` component before independent sign-off.

## Mandatory automated security tests

Present from the first component that needs them (Layer 2 onward) and never removed:

1. **Hybrid-downgrade test.** Strip the PQC component from a real hybrid signature, alter the declared-mode byte, call `verify()` — must return `False` before any further crypto executes.
2. **Replay rejection.** Consume a challenge/token/backup-code/push-approval once, attempt reuse — must be rejected via `ReplayStore` consume-once semantics.
3. **Rate-limit rejection.** Both per-identity and global limiters must independently trip and reject.
4. **KEM ciphertext/public-key substitution test.** Swap either value post-encapsulation — must fail, because both are bound into the HKDF `info` parameter.
5. **Wire-parser fuzzing.** Property-based tests (e.g. Hypothesis) against every length-prefixed binary parser, with malformed and adversarially-sized length fields — not just the deterministic cases above.

Any new Layer 2+ component that introduces a new attack surface gets its own test in this category before merge, not after.

## Review gates (`GATE_REVIEW_REQUIRED`)

Components requiring independent (not self-) sign-off before "production-ready" status, logged in `docs/adr/`:

- `SignatureCombiner`, `KEMCombiner`
- `AlgorithmRegistry`
- `KeyWallet` backends (`EncryptedFileBackend`, `OSKeychainBackend`, `HsmPkcs11Backend`)
- `ThresholdPolicy` / `ThresholdManager`
- `MerkleMembershipProof`, `AnonymousProofBackend`

A reviewer cannot sign off a component they authored — independence is the point. Review happens as soon as a component is built, in build order (`02-build-order.md`) — not batched to the end.

## PQC backend statement

Every piece of material — doc, README, pitch deck, client proposal — that references a PQC adapter states plainly which library backs it (`cryptography` (pyca) `>=48,<51`), that its ML-KEM and ML-DSA support is recent, and that QuantX makes no FIPS-validation claim for the PQC implementation unless the specific backend build in use is itself validated. This isn't a one-time disclaimer; it's checked per-artifact. Supersedes the `liboqs` research-grade disclosure (D-006, accepted; D-010 pin policy).

## Secrets & config management

- `AlgorithmRegistry` config: unsigned only for dev (`allow_unsigned=True`); the signed-config path is built from the start (`02-build-order.md`, Layer 3) and is what any non-dev deployment uses.
- Key custody vault metadata is authenticated (included in AEAD AAD), not just the key material itself.
- Dependency pinning + CI-run `ruff`/`black`/`mypy --strict` on every change — a security requirement as much as a quality one, since an unpinned crypto dependency is a supply-chain risk.

## Backend failure modes are security-relevant, not just reliability concerns

- A `KeyValueStore` backend's network/connection failure has a stated fail-closed-vs-degrade decision — silently degrading a replay/rate-limit backend under load is a security bug, not just an availability one.
- `HsmPkcs11Backend`/`OSKeychainBackend` unavailability raises explicit typed errors rather than silently behaving like a weaker in-memory store — a silent fallback here would be a custody downgrade, not a UX issue.

## Security requirements register

Every item here is enforced from the moment its component is built, per `02-build-order.md`. Grouped by severity of consequence if violated, for review-prioritization purposes only — not by when they were "found."

**Critical**

| ID | Requirement | Enforced in |
|---|---|---|
| SR-1 | Mode is never accepted from client-declared/wire data — `required_mode` is a server-side construction fact, checked before any cryptographic verification runs | `SignatureCombiner`, sidecar `/verify` |
| SR-2 | A membership-proof verifier actually walks the authentication path to the root and checks it — never a fixed/placeholder result | `MerkleMembershipProof` |

**High**

| ID | Requirement | Enforced in |
|---|---|---|
| SR-3 | In-memory store has a hard `max_entries` cap — never unbounded | `InMemoryKVStore` |
| SR-4 | Networked backend failure has a stated, implemented fail-closed-vs-degrade decision — never an unhandled exception | `RedisKVStore` or equivalent |
| SR-5 | Push-notification issuance is rate-limited before sending, not just verification | `PushAuthenticator` |
| SR-6 | Custody backends provide a real integration or raise an explicit typed error — never a silent fallback to weaker storage | `HsmPkcs11Backend`, `AwsKmsBackend`, `GcpKmsBackend`, `OSKeychainBackend`. Production custody is key-resident (D-008) |

**Medium**

| ID | Requirement | Enforced in |
|---|---|---|
| SR-7 | KEM ciphertext and public key are bound into the HKDF `info` parameter, so substitution is cryptographically detectable | `KEMCombiner` |
| SR-8 | Exactly one canonicalization path is used for anything signed, system-wide | `JCSCanonicalizer` |
| SR-9 | Vault metadata is included in AEAD AAD; corruption raises explicitly rather than returning empty | `EncryptedFileBackend` |
| SR-10 | Session token is minted only as the final statement after every required gate passes — no exception path leaves a live token behind | `SessionOrchestrator` |
| SR-11 | Push/backup-code approvals are consumed through `ReplayStore` — single use, no replay | `PushAuthenticator`, `BackupCodeManager` |
| SR-12 | Duplicate keys in a threshold policy are rejected at policy-creation time, not at finalize time | `ThresholdPolicy` |
| SR-13 | TLS inspection findings are tagged by trust level (`verified` vs `unverified`); an unauthenticated probe is never presented as equivalent to an authenticated one | `TlsInspector` |

**Low**

| ID | Requirement | Enforced in |
|---|---|---|
| SR-14 | Timestamps come only from an injected `Clock`, never `or`-defaulted against wall-clock reads | Every timestamp-consuming component |
| SR-15 | Static-scan findings ship with a permanent best-effort/false-positive-and-negative disclaimer attached to the output itself, not just the README | `StaticSourceScanner` |

## Configuration and delivery requirements

The configuration rules CFG-1 to CFG-8 (`15-config-and-composition.md`) and the delivery rules SLICE-1 to SLICE-7 (`16-delivery-and-factory.md`) are security-relevant: config fails closed, secrets never sit in the config file, and a build is never labelled reviewed without a sign-off record. They are tracked in those documents and tested in `service/tests/` and `factory/tests/`.

## What this doc does not cover

Physical security, personnel security, and legal/contractual security terms for client engagements — those belong to the consulting practice's operating procedures and client SOWs, not this codebase's security requirements.
