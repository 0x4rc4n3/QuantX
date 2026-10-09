# `conftest.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for session tests — a wired `SessionOrchestrator` using real Layer 0-2 components, plus a fake `Clock` for deterministic TTL/rate-limit-window testing.

## Part of / dependency graph
- **Package:** `quantx-session`, `tests/`
- **Depends on:** Every `src/` file in this package plus the Layer 0-2 components it wires
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 4
- **Depends on:** This package's `src/` plus Layer 0-2.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction.
- **Security notes:** The fake `Clock` fixture is a precondition for deterministic expiry/rate-limit testing.

## Required behavior
- Provides a wired `SessionOrchestrator` and `ChallengeIssuer` using real Layer 0-2 components and a fake `Clock`.

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
