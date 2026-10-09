# `test_encrypted_file_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `EncryptedFileBackend`'s genuine store/retrieve round trip, on the non-adversarial path.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/backends/`
- **Depends on:** `encrypted_file_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** encrypted_file_backend.py
- **Implements:** pytest test functions.
- **Outside:** Other backends' mechanics.
- **Inside:** This backend's genuine store/retrieve round trip.
- **Security notes:** See Security notes below.

## Required behavior
- `store` → `retrieve` round-trips key material and metadata correctly.
- SR-9's AAD-authentication and corruption-handling adversarial scenarios are separate security tests, not duplicated here.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `encrypted_file_backend.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Other backends.

## Source docs
`04-functional-requirements.md`
