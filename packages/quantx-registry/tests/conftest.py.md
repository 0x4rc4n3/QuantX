# `conftest.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for registry tests — a real example YAML config (both signed and unsigned variants) and a wired-up signing keypair for testing `registry_config_signature.py`.

## Part of / dependency graph
- **Package:** `quantx-registry`, `tests/`
- **Depends on:** `algorithm_registry.example.yaml`; every `src/` file in this package
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 3
- **Depends on:** Every file in this package.
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction: signed/unsigned config variants.
- **Security notes:** The unsigned-config fixture is what makes `test_unsigned_config_rejected_when_signing_required.py` a real test.

## Required behavior
- Provides a signed and an unsigned variant of an example config for tests to load under different `allow_unsigned` settings.

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
