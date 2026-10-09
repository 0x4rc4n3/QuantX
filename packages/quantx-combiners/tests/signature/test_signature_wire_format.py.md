# `test_signature_wire_format.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `signature_wire_format.py`'s `encode`/`decode` round-trip and length-prefix bounds-checking on deterministic (non-fuzzed) inputs.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/`
- **Depends on:** `signature_wire_format.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 2
- **Depends on:** `signature_wire_format.py`
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- `encode` → `decode` round-trips for every mode's component shape.
- A hand-crafted truncated buffer is rejected as malformed, not read out of bounds.
- Property-based/adversarial fuzzing of this same parser is `test_signature_wire_format_fuzz.py`'s job, not duplicated here.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the deterministic unit test for `signature_wire_format.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside this file's named subject.

## Source docs
`14-directory-structure.md`, `13-error-and-edge-cases.md`
