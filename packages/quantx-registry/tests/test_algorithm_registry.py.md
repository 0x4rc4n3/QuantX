# `test_algorithm_registry.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `AlgorithmRegistry.resolve()` correctly wires a role name to a constructed combiner pair with the correct `required_mode`, and fails fast on an unregistered algorithm reference.

## Part of / dependency graph
- **Package:** `quantx-registry`, `tests/`
- **Depends on:** `algorithm_registry.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 3
- **Depends on:** algorithm_registry.py
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- Resolving a valid role name returns a correctly-wired combiner + `required_mode`.
- A role referencing an unregistered algorithm fails at load/startup time, not first use.
- Confirms this is the only file directly importing Layer-1 adapters, per FR-3.1 (cross-checked at the import-lint level by `tools/lint/check_no_sibling_imports.py`, not re-implemented as a runtime check here).

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `algorithm_registry.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside `algorithm_registry.py`.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`
