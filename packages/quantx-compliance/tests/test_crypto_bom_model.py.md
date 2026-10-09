# `test_crypto_bom_model.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `CryptoBOM`'s shape holds findings with source/trust-level/disclaimer attribution correctly.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/`
- **Depends on:** `crypto_bom_model.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `crypto_bom_model.py`
- **Implements:** pytest test functions.
- **Outside:** Scanner behavior.
- **Inside:** Data-model shape.
- **Security notes:** None — structural only.

## Required behavior
- A `CryptoBOM` constructed with findings preserves each finding's source, trust level, and any attached disclaimer.

## Inputs / outputs
- **In:** sample findings.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `crypto_bom_model.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Scanner behavior.

## Source docs
`04-functional-requirements.md`
