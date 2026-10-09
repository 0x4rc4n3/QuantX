# `conftest.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared `pytest` fixtures for every test in `quantx-core/tests/` — a fake/injectable `Clock`, a fresh `InMemoryKVStore` per test, and any other Layer-0 fixture reused across multiple test files.

## Part of / dependency graph
- **Package:** `quantx-core`, `tests/`
- **Depends on:** Everything under `src/quantx_core/` this package's tests need fixtures for.
- **Imported by:** Every test file in this package, implicitly, per `pytest` convention.

## Docstring contract
- **Layer:** 0
- **Depends on:** The Layer-0 interfaces and impls being fixture-wrapped.
- **Implements:** pytest fixtures, not production code.
- **Outside:** Test logic itself — fixtures only, no assertions live here.
- **Inside:** Fixture construction and teardown.
- **Security notes:** A fake `Clock` fixture here is what makes SR-14 (`test_sr_14_clock_never_defaults.py`) and expiry-dependent tests deterministic rather than flaky against real wall-clock time.

## Required behavior
- Provides a controllable fake `Clock` fixture so tests can advance time deterministically (needed for TTL-expiry and rate-limit-window tests).
- Provides a fresh `InMemoryKVStore` fixture per test, so tests don't leak state into each other.

## Inputs / outputs
- **In:** nothing (fixtures are constructed, not passed input).
- **Out:** fixture objects injected into test function parameters.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- A deterministic fake `Clock` here is a precondition for `test_sr_14_clock_never_defaults.py` being a meaningful test rather than a flaky one.

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package that consumes its fixtures.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any assertion logic — this file only constructs fixtures.

## Source docs
`14-directory-structure.md`
