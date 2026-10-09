# `quantx-registry/tests/security/`

## What this is
The registry's one dedicated security test: unsigned config rejected when signing is required.

## Part of
`quantx-registry`, Layer 3.

## Contains
- `test_unsigned_config_rejected_when_signing_required.py`

## Why divided this way
A foundational, cross-cutting test rather than one tied to a single numbered `SR-x` item, per `14-directory-structure.md`'s stated exception to the `test_sr_<NN>_*` naming convention.

## Dependency rules
- Depends on `algorithm_registry.py` and `registry_config_signature.py` together.

## Source docs
`14-directory-structure.md`, `04-functional-requirements.md`
