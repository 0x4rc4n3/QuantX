# `test_merkle_membership_proof.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `verify()` accepts a genuine membership proof and rejects a tampered one, on the non-adversarial/structural path (the SR-2 "actually walks the path, not a lookup-table stub" scenario is the dedicated security test).

## Part of / dependency graph
- **Package:** `quantx-zkp`, `tests/`
- **Depends on:** `merkle_membership_proof.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 9
- **Depends on:** `merkle_membership_proof.py`
- **Implements:** pytest test functions.
- **Outside:** SR-2's specific stub-detection scenario — separate file.
- **Inside:** Genuine accept/reject behavior.
- **Security notes:** See Security notes below.

## Required behavior
- A genuine path for a real member verifies successfully against the tree's real root.
- A tampered path (one sibling hash altered) fails verification.

## Inputs / outputs
- **In:** genuine and tampered paths.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the structural unit test for `merkle_membership_proof.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-2's stub-detection scenario — separate file.

## Source docs
`04-functional-requirements.md`
