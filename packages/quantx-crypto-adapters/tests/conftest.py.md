# `conftest.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared `pytest` fixtures for adapter tests — primarily keypair-generation helpers so every adapter test doesn't reimplement its own keygen boilerplate.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `tests/`
- **Depends on:** Every adapter under `src/quantx_crypto_adapters/`.
- **Imported by:** Every test file in this package, implicitly, per `pytest` convention.

## Docstring contract
- **Layer:** 1
- **Depends on:** Every adapter this package's tests exercise.
- **Implements:** pytest fixtures, not production code.
- **Outside:** Test assertions themselves.
- **Inside:** Fixture construction (keypairs, sample messages).
- **Security notes:** None beyond what individual test files declare.

## Required behavior
- Provides keypair-generation fixtures, parametrizable per algorithm, so `test_verify_fails_closed_on_malformed_input.py` can run the same scenario against every adapter without duplicating setup.

## Inputs / outputs
- **In:** nothing.
- **Out:** fixture objects (keypairs, sample messages) injected into test functions.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any assertion logic.

## Source docs
`14-directory-structure.md`
