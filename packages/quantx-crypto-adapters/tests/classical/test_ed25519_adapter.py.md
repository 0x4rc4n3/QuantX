# `test_ed25519_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ed25519_adapter.py` round-trips correctly and satisfies its `Signer/Verifier` contract for Ed25519.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `tests/classical/`
- **Depends on:** `ed25519_adapter.py` (the file under test)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 1
- **Depends on:** ed25519_adapter.py
- **Implements:** pytest test functions.
- **Outside:** Any adapter other than this one.
- **Inside:** Ed25519 round-trip and negative-path scenarios.
- **Security notes:** See Security notes below.

## Required behavior
- `generate_keypair → sign/encapsulate → verify/decapsulate` round-trips correctly for a genuine keypair/message (`02-build-order.md` Layer-1 definition of done).
- A tampered signature/ciphertext or wrong key fails verification/decapsulation.

## Inputs / outputs
- **In:** generated keypairs and sample messages from `conftest.py`.
- **Out:** pass/fail per assertion.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Malformed input is covered by the shared `test_verify_fails_closed_on_malformed_input.py`, not duplicated here.

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the round-trip test for `ed25519_adapter.py`.

## Non-negotiable principles that apply
- **P2.** One algorithm per adapter file, forever.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any algorithm other than Ed25519.

## Source docs
`04-functional-requirements.md`, `02-build-order.md`
