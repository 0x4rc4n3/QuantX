# `test_hsm_pkcs11_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `HsmPkcs11Backend`'s genuine store/retrieve round trip against the SoftHSM2 dev token provisioned by `tools/softhsm2/setup_softhsm2_dev_token.sh`.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/backends/`
- **Depends on:** `hsm_pkcs11_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** hsm_pkcs11_backend.py
- **Implements:** pytest test functions.
- **Outside:** Other backends' mechanics.
- **Inside:** This backend's genuine store/retrieve round trip.
- **Security notes:** See Security notes below.

## Required behavior
- `store` → `retrieve` round-trips against the SoftHSM2 PKCS#11 module.
- Confirms this is a real integration, not a stub — per FR-6.5's requirement that this backend either really works or explicitly errors.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `hsm_pkcs11_backend.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Other backends.

## Source docs
`02-build-order.md`, `04-functional-requirements.md`
