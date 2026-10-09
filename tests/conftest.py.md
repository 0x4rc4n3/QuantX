# `conftest.py`

**Package:** `root tests` · **Layer:** cross-cutting · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Builds a full-stack fixture — Recipe A via `default_setup()`, plus every Layer 5-10 component the end-to-end SR tests need — so each `test_sr_<NN>_end_to_end_*.py` file doesn't have to re-wire the whole system itself.

## Part of / dependency graph
- **Package:** `root tests`, `tests/`
- **Depends on:** `default_setup.py` (Layer 4) and every package the 15 end-to-end tests collectively exercise
- **Imported by:** Every file under `tests/security/`, implicitly.

## Docstring contract
- **Layer:** cross-cutting
- **Depends on:** The full stack, Layers 0-10.
- **Implements:** pytest fixtures.
- **Outside:** Assertions themselves.
- **Inside:** Full-stack fixture construction.
- **Security notes:** This fixture's correctness is a precondition for every end-to-end SR test being a meaningful test of the *wired* system, not just of individual packages in isolation.

## Required behavior
- Provides a fully-wired system (Recipe A, or the minimal wiring each SR scenario needs across packages) for the 15 end-to-end tests to exercise.

## Inputs / outputs
- **In:** nothing.
- **Out:** fixture objects representing the full wired stack.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every file in `tests/security/`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Assertion logic.

## Source docs
`14-directory-structure.md`
