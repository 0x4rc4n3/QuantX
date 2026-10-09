# `conftest.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for threshold tests — a valid multi-key policy and a wired `SignatureCombiner` for producing genuine approvals to submit.

## Part of / dependency graph
- **Package:** `quantx-threshold`, `tests/`
- **Depends on:** Every `src/` file in this package plus `signature_combiner.py` (Layer 2)
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 8
- **Depends on:** This package's `src/`, Layer 2.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction.
- **Security notes:** None beyond individual test files' own.

## Required behavior
- Provides a valid `ThresholdPolicy` and a helper for producing genuine, verifiable approvals.

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
