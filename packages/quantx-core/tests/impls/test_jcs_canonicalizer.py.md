# `test_jcs_canonicalizer.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `JCSCanonicalizer.canonicalize()` produces deterministic, RFC-8785-compliant bytes regardless of input key order.

## Part of / dependency graph
- **Package:** `quantx-core`, `packages/quantx-core/tests/impls`
- **Depends on:** ``jcs_canonicalizer.py`` (the file under test)
- **Imported by:** Nothing — test files are leaves in the dependency graph.

## Docstring contract
- **Layer:** 0
- **Depends on:** `jcs_canonicalizer.py`
- **Implements:** pytest test functions, not a production interface.
- **Outside:** Testing anything other than the one file/behavior named in this spec's title.
- **Inside:** The scenarios listed under Required behavior below.
- **Security notes:** See Security notes section below.

## Required behavior
- Two logically-equal mappings with different key insertion order canonicalize to identical bytes.
- Output is stable/reproducible across repeated calls with the same input.

## Inputs / outputs
- **In:** fixtures from `conftest.py` plus any test-local fixtures.
- **Out:** pass/fail per `pytest` assertion; no production return value.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `JCSCanonicalizer`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Testing any file other than the one named in this spec's title.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
