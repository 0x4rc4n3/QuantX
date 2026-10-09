# `conftest.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for wallet tests — a temp-directory `EncryptedFileBackend`, and (where the environment provides it) a SoftHSM2-backed `HsmPkcs11Backend` fixture.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/`
- **Depends on:** Every `src/` file in this package
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 6-7
- **Depends on:** This package's `src/`.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction, including SoftHSM2 dev-token wiring.
- **Security notes:** The corrupted-vault fixture here is a precondition for `test_vault_corruption_raises_not_silent_empty.py`.

## Required behavior
- Provides a temp-directory `EncryptedFileBackend`, a SoftHSM2-backed `HsmPkcs11Backend` fixture, and a helper for producing a deliberately corrupted vault file.

## Inputs / outputs
- **In:** nothing.
- **Out:** fixture objects.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Assertion logic.

## Source docs
`14-directory-structure.md`, `02-build-order.md`
