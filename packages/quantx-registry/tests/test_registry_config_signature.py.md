# `test_registry_config_signature.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `sign`/`verify` round-trip correctly over canonicalized config bytes, and that a tampered config fails verification.

## Part of / dependency graph
- **Package:** `quantx-registry`, `tests/`
- **Depends on:** `registry_config_signature.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 3
- **Depends on:** registry_config_signature.py
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- A signed config verifies successfully against its own signature.
- A tampered config (single byte changed) fails verification.
- Uses `Canonicalizer.canonicalize()` as the only path to bytes-before-signing (FR-0.4) — confirmed here, not re-derived ad hoc.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `registry_config_signature.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside `registry_config_signature.py`.

## Source docs
`04-functional-requirements.md`, `09-auth-and-authorization.md`
