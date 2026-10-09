# QuantX — User Stories & Flows

**Status:** Pre-implementation · **Depends on:** `06-system-architecture.md` for exact call signatures — flows below are sequence-level, not wire-level. Organized by build-order layer (`02-build-order.md`), not by phase — there are no phases.

## Personas

| Persona | Who they are | What they touch |
|---|---|---|
| **Integrator** | Developer wiring QuantX into a client system, or you during a client engagement | Package APIs, `AlgorithmRegistry`, composition recipes |
| **Subject** | The human or service that ultimately authenticates | Never touches QuantX directly — experiences it through the client's app |
| **Relying-party operator** | Runs the verifying side of a deployment | `SessionOrchestrator` config, MFA policy, key-custody choice |
| **Reviewer** | Internal or third-party independent reviewer | `GATE_REVIEW_REQUIRED` checklists, compliance reports (Layer 10) |
| **Consulting operator** | You, composing a bespoke solution per client | All of the above, per D3's business model |

## Layer 4 — Core session engine

**Story:** As an Integrator, I wire Recipe A and get a working hybrid-auth demo without touching any component's internals.

```
Integrator                 QuantX
    |--- default_setup() ----->|   (constructs clock, kv, canon, registry, combiner, orchestrator)
    |<-- orchestrator, totp ---|
    |--- start(subject_id) --->|   ChallengeIssuer builds a challenge, stored via kv
    |<-- challenge -------------|
    |--- finish(signed) ------->|  SignatureCombiner verifies against required_mode (server-set, never trusted from wire)
    |<-- session token ---------|  (only minted after every gate passes — no exception path leaves a live token)
    |--- validate(token) ------>|  ReplayStore / rate limiter checked
    |<-- valid / invalid -------|
```

**Story:** As a security reviewer, I need to see the downgrade attack fail. Strip the PQC component off a real HYBRID signature, rewrite the declared-mode byte, call `verify()` — it must return `False`, unconditionally, before any further crypto runs (SR-1).

## Layer 5 — Second factor

**Story:** As a relying-party operator, I add TOTP as an additional gate in `SessionOrchestrator` without changing anything about how the primary PQC/hybrid factor works.

```
Subject                    Orchestrator              TotpProvider
   |-- primary auth (Layer 4 flow) -->|
   |<---------- primary factor OK ----|
   |-- TOTP code -------------------->|-- verify(code) -->|
   |                                  |<-- ok/rate-limited-|
   |<---------- session token --------|
```

**Story:** As an attacker, if I hammer the TOTP endpoint, I get rate-limited per-identity — this is its own test, not inherited implicitly from the Layer 4 limiter.

**Note on sequencing:** TOTP *verification* logic is built as soon as Layer 5 is reached, against test-fixture secrets. Durable secret storage is wired through as soon as Layer 6 (`KeyWallet`) exists (D11) — this is a real dependency, not a deferral.

## Layer 6–7 — Key custody & recovery

**Story:** As a relying-party operator, my subjects' keys survive a process restart. `KeyWallet` backed by `EncryptedFileBackend` — vault metadata is AAD-authenticated; if the file is corrupted, I get a raised error, not a silent empty result (SR-9).

**Story:** As a subject who lost my device, I use a backup code. Each code is single-use-verified — replaying a consumed code fails the same way replaying a session challenge fails (SR-11).

**Story:** As an operator without client-specific HSM hardware yet, I still get a real `HsmPkcs11Backend` to build and test against, using SoftHSM2 as the development target (`02-build-order.md`) — not a stub that silently behaves like plaintext storage.

## Layer 0–4 (scaling) — Production-grade backends

**Story:** As an operator scaling from one process to many, I change one constructor argument (`InMemoryKVStore` → a networked backend) and nothing else in the system changes. This is the literal test of the architecture's core promise — if any other component needs to change, that's a bug in the architecture, not a feature request.

## Layer 8 — Governance

**Story:** As a client with board-level approval requirements, my high-value action needs N-of-M sign-off before it executes.

```
Approver 1 --sign-->|
Approver 2 --sign-->|--> ThresholdManager.finalize() --> checks quorum + duplicate-key rejection (SR-12) --> action executes
Approver 3 (not needed, quorum already met)
```

**Story:** As a reviewer, I confirm two approvers can't reuse the same key to count as two signatures — `ThresholdPolicy` rejects duplicate keys at policy creation, not after the fact.

## Layer 9 — Membership proofs

**Story:** As a client, I need to prove a subject is a member of a set without revealing extra data about them — but I need it to be honest about what it actually guarantees.

**Story:** As a reviewer, I check that `MerkleMembershipProof` actually walks the path to the root (SR-2) and that any UI or doc surfacing this makes the "sound but non-anonymous" caveat impossible to miss. `AnonymousProofBackend` stays `NotImplementedError` until a funded, scoped audit exists for whatever's plugged in — this gate is about audit availability, not build order (`02-build-order.md`).

## Layer 10 — Observability & compliance

**Story:** As a client's security team, I run a crypto-inventory scan across our codebase and TLS endpoints and get a report tagged by trust level — the `StaticSourceScanner`'s output carries upfront that it produces best-effort results with real false positives/negatives (SR-15), and the `TlsInspector` output tells me which findings came from an authenticated probe versus a permissive one (SR-13).

```
Source code / TLS endpoints --> Scanners --> CryptoBOMModel entries --> ComplianceReportGenerator --(+ StandardsCatalog)--> report
```

## Packaging & first external use

**Story:** As a client or collaborator, I `pip install` whichever QuantX packages are ready and point my app at the REST sidecar's `/challenge`, `/verify`, `/session/:id` endpoints without needing the Python SDK directly. See `08-api-specification.md` for the contract.

**Story:** As the consulting operator, I get a demoable artifact as soon as Layer 4 is done — packaging isn't held back until every layer is finished (`02-build-order.md`).
