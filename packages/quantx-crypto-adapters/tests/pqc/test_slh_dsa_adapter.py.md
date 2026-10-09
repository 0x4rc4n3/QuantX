# `test_slh_dsa_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** specified, **blocked on upstream** (D-006) — not created until `cryptography` ships SLH-DSA.

## Purpose
Verifies `slh_dsa_adapter.py` round-trips correctly and satisfies its `Signer/Verifier` contract for SLH-DSA (pyca-backed once available).

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `tests/pqc/`
- **Depends on:** `slh_dsa_adapter.py` (the file under test)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 1
- **Depends on:** slh_dsa_adapter.py
- **Implements:** pytest test functions.
- **Outside:** Any adapter other than this one.
- **Inside:** SLH-DSA round-trip and negative-path scenarios.
- **Security notes:** Blocked until pyca ships SLH-DSA (D-006); no other library may back it.

## Required behavior
- `generate_keypair → sign/encapsulate → verify/decapsulate` round-trips correctly for a genuine keypair/message (`02-build-order.md` Layer-1 definition of done).
- A tampered signature/ciphertext or wrong key fails verification/decapsulation.

## Inputs / outputs
- **In:** generated keypairs and sample messages from `conftest.py`.
- **Out:** pass/fail per assertion.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Malformed input is covered by the shared `test_verify_fails_closed_on_malformed_input.py`, not duplicated here.

## Security notes
- Any material referencing this adapter states it is not yet available, and why (D-006).

## Mandatory tests this must pass
- This file is itself the round-trip test for `slh_dsa_adapter.py`.

## Non-negotiable principles that apply
- **P2.** One algorithm per adapter file, forever.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any algorithm other than SLH-DSA.

## Source docs
`04-functional-requirements.md`, `02-build-order.md`, `10-security-requirements.md`
