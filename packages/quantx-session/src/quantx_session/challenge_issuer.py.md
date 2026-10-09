# `challenge_issuer.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Issues a challenge for a subject to sign — stores it via `KeyValueStore` rather than holding it in process memory (FR-4.1), the `start()` half of the `default_setup() → start() → finish() → validate()` demo flow.

## Part of / dependency graph
- **Package:** `quantx-session`, `src/quantx_session`
- **Depends on:** `quantx_core.interfaces.key_value_store.KeyValueStore` (Layer 0); `quantx_core.interfaces.clock.Clock` (Layer 0); `quantx_core.interfaces.canonicalizer.Canonicalizer` (Layer 0, FR-0.4); `challenge_record.py` (this package)
- **Imported by:** `session_orchestrator.py`, `default_setup.py` (this package); `service/src/quantx_service/routers/challenge_router.py`

## Docstring contract
- **Layer:** 4
- **Depends on:** `KeyValueStore`, `Clock`, `Canonicalizer` (Layer 0); `ChallengeRecord` (this package)
- **Implements:** `issue(subject_id: str) -> ChallengeRecord`
- **Outside:** Verifying the signed response — `SessionOrchestrator`'s job.
- **Inside:** Constructing a `ChallengeRecord` (nonce, `issued_at`/`expires_at` via `Clock`, `required_mode` set server-side) and persisting it through `KeyValueStore`.
- **Security notes:** FR-4.1: stored via `KeyValueStore`, never held in process memory outside that interface. `required_mode` set here is never later overridden by anything wire-derived (SR-1).

## Required behavior
- Produces a challenge that is stored via `KeyValueStore`, not held in process memory outside that interface (FR-4.1).
- The nonce is canonicalized via `Canonicalizer.canonicalize()` before it's ever signed by a subject (FR-0.4) — no ad hoc serialization.
- `issued_at`/`expires_at` come from the injected `Clock`, never a direct wall-clock read (FR-0.3, SR-14).
- `required_mode` is set here, server-side, at issuance — never trusted from a later client message (SR-1, `07-database-design.md`).
- Challenges are short-lived (TTL-backed) and expire unconsumed automatically at the backend level where supported, or via explicit expiry check (`07-database-design.md`).

## Inputs / outputs
- **In:** `subject_id: str`.
- **Out:** a `ChallengeRecord` containing `challenge_id`, `nonce`, `issued_at`, `expires_at`, and `required_mode`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A session token is requested before all configured factors have passed → out of this file's scope (that's `SessionOrchestrator`'s job) but the challenge this file issues is one input to that gate.

## Security notes
- **FR-4.1.** No ad hoc in-process cache — `KeyValueStore` only.
- **SR-1 (issuance side).** `required_mode` is fixed here, server-side.

## Mandatory tests this must pass
- `tests/test_challenge_issuer.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Verifying any signed response — `session_orchestrator.py`.
- Deciding which algorithm pairing/`required_mode` a role uses — that's `AlgorithmRegistry` (Layer 3), consulted by whoever wires this class.

## Source docs
`04-functional-requirements.md`, `07-database-design.md`, `10-security-requirements.md`, `03-user-stories-and-flows.md`
