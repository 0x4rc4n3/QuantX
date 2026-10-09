# `test_ml_kem_768_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ml_kem_768_adapter.py` round-trips correctly and satisfies its `KEMProvider` contract for ML-KEM-768, `cryptography`-backed.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `tests/pqc/`
- **Depends on:** `ml_kem_768_adapter.py` (the file under test)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 1
- **Depends on:** ml_kem_768_adapter.py
- **Implements:** pytest test functions.
- **Outside:** Any adapter other than this one.
- **Inside:** ML-KEM-768 round-trip and negative-path scenarios.
- **Security notes:** The PQC backend statement (D-006) applies to this file's subject (`cryptography`-backed).

## Required behavior
- `generate_keypair → sign/encapsulate → verify/decapsulate` round-trips correctly for a genuine keypair/message (`02-build-order.md` Layer-1 definition of done).
- A tampered ciphertext or wrong key yields a *different* shared secret (ML-KEM implicit rejection); the test asserts inequality, not an exception. A wrong-length ciphertext fails closed.
- The adapter returns `(ciphertext, shared_secret)` in the Layer-0 order, not pyca's reversed order.

## Inputs / outputs
- **In:** generated keypairs and sample messages from `conftest.py`.
- **Out:** pass/fail per assertion.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Malformed input is covered by the shared `test_verify_fails_closed_on_malformed_input.py`, not duplicated here.

## Security notes
- Any material referencing this adapter states the backing library and its maturity per the PQC backend statement (D-006, `10-security-requirements.md`) — this isn't a one-time disclaimer, it's checked per-artifact.

## Mandatory tests this must pass
- This file is itself the round-trip test for `ml_kem_768_adapter.py`.

## Non-negotiable principles that apply
- **P2.** One algorithm per adapter file, forever.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any algorithm other than ML-KEM-768.

## Source docs
`04-functional-requirements.md`, `02-build-order.md`, `10-security-requirements.md`
