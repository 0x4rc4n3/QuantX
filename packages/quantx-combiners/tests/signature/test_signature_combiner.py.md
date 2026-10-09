# `test_signature_combiner.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `SignatureCombiner`'s orchestration: correct pass/fail across HYBRID, PQC_ONLY, and CLASSICAL_ONLY modes, using genuine (non-adversarial) inputs.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/`
- **Depends on:** `signature_combiner.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 2
- **Depends on:** `signature_combiner.py`
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- A genuine signature under each of the three modes verifies successfully.
- A tampered (but shape-consistent) signature fails verification.
- Confirms `signature_mode_enforcement.py` is actually called before any `Verifier` — the adversarial downgrade scenario itself is `test_sr_01_hybrid_downgrade_rejected.py`'s job, not duplicated here.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the integration test for `signature_combiner.py`'s non-adversarial behavior.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside this file's named subject.

## Source docs
`04-functional-requirements.md`
