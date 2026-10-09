# `conftest.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for combiner tests — wired-up `SignatureCombiner`/`KEMCombiner` instances using real Layer-1 adapters, plus helpers for constructing a genuine hybrid signature/KEM exchange that individual tests can then tamper with.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/`
- **Depends on:** Every adapter in `quantx-crypto-adapters`, both combiner classes
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 2
- **Depends on:** Layer-1 adapters, both combiner classes.
- **Implements:** pytest fixtures.
- **Outside:** Assertions themselves.
- **Inside:** Fixture construction, including a genuine-hybrid-signature helper for the downgrade test to tamper with.
- **Security notes:** The genuine-hybrid fixture is a precondition for `test_sr_01_hybrid_downgrade_rejected.py` and `test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py` being real tests rather than synthetic ones.

## Required behavior
- Provides a wired `SignatureCombiner` and `KEMCombiner` using real adapters.
- Provides a helper producing a genuine HYBRID signature/KEM exchange, so security tests tamper with something real rather than a synthetic stand-in.

## Inputs / outputs
- **In:** nothing.
- **Out:** fixture objects.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Assertion logic.

## Source docs
`14-directory-structure.md`
