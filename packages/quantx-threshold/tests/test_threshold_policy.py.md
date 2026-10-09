# `test_threshold_policy.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ThresholdPolicy` accepts a valid distinct-key set and rejects an out-of-range `m`, on the non-adversarial/structural-validation path (duplicate-key rejection is the dedicated SR-12 test).

## Part of / dependency graph
- **Package:** `quantx-threshold`, `tests/`
- **Depends on:** `threshold_policy.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 8
- **Depends on:** `threshold_policy.py`
- **Implements:** pytest test functions.
- **Outside:** SR-12 duplicate-key rejection — separate file.
- **Inside:** Valid-construction and `m`-range validation.
- **Security notes:** None beyond structural validation.

## Required behavior
- A valid, distinct-key set with a sane `m` constructs successfully.
- An `m` outside the valid range (e.g. `m > n` or `m < 1`) is rejected at construction.

## Inputs / outputs
- **In:** key sets and `m` values.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the structural unit test for `threshold_policy.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-12 duplicate-key rejection — separate file.

## Source docs
`04-functional-requirements.md`
