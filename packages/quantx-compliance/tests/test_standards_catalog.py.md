# `test_standards_catalog.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `standards_catalog.py`'s lookup returns the expected reference set for a known algorithm.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/`
- **Depends on:** `standards_catalog.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `standards_catalog.py`
- **Implements:** pytest test functions.
- **Outside:** Report formatting.
- **Inside:** Lookup correctness.
- **Security notes:** None.

## Required behavior
- `lookup(algorithm_id)` returns the expected static reference set for a known algorithm.

## Inputs / outputs
- **In:** an `AlgorithmId`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `standards_catalog.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Report formatting.

## Source docs
`04-functional-requirements.md`
