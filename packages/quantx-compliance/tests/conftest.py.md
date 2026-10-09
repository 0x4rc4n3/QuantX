# `conftest.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for compliance tests — a sample `CryptoBOM` with mixed authenticated/unverified TLS findings, and a temp source tree for the static scanner to run against.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/`
- **Depends on:** Every `src/` file in this package
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 10
- **Depends on:** This package's `src/`.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction.
- **Security notes:** None beyond individual test files' own.

## Required behavior
- Provides a sample `CryptoBOM` and a temp source tree with known crypto-usage patterns for the static scanner to find.

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
`14-directory-structure.md`
