# `conftest.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for authenticator tests — test-fixture TOTP/HOTP secrets (per D11, real `KeyWallet`-backed storage is exercised in `quantx-wallet`'s own tests, not here) and a fake `Clock`.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/`
- **Depends on:** Every `src/` file in this package
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 5
- **Depends on:** This package's `src/`.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction.
- **Security notes:** None beyond individual test files' own.

## Required behavior
- Provides test-fixture TOTP/HOTP secrets and a fake `Clock` for deterministic code verification.

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
`14-directory-structure.md`, `00-index.md`
