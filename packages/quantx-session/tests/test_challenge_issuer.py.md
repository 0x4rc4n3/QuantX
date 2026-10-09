# `test_challenge_issuer.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ChallengeIssuer.issue()` stores a correctly-shaped `ChallengeRecord` via `KeyValueStore`, with `required_mode` fixed server-side.

## Part of / dependency graph
- **Package:** `quantx-session`, `tests/`
- **Depends on:** `challenge_issuer.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 4
- **Depends on:** `challenge_issuer.py`
- **Implements:** pytest test functions.
- **Outside:** Session orchestration itself.
- **Inside:** Challenge issuance and storage behavior.
- **Security notes:** Confirms FR-4.1/SR-1 at the issuance boundary.

## Required behavior
- `issue(subject_id)` returns a `ChallengeRecord` with a `challenge_id`, `nonce`, `issued_at`/`expires_at` from the injected `Clock`, and a server-fixed `required_mode`.
- Confirms the issued challenge is retrievable via `KeyValueStore.get()`, not held only in process memory.
- Confirms `nonce` was passed through `Canonicalizer.canonicalize()`.

## Inputs / outputs
- **In:** `subject_id`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `challenge_issuer.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- `session_orchestrator.py`'s own behavior.

## Source docs
`04-functional-requirements.md`, `07-database-design.md`
