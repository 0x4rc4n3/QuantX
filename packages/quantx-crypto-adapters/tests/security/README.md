# `quantx-crypto-adapters/tests/security/`

## What this is
The one shared security test owned by Layer 1: fail-closed behavior on malformed input, parametrized across every adapter (FR-0.1).

## Part of
`quantx-crypto-adapters`, Layer 1.

## Contains
- `test_verify_fails_closed_on_malformed_input.py` — FR-0.1, parametrized across every adapter

## Why divided this way
A single parametrized file rather than eight near-identical ones, because the scenario (malformed input → fail closed, never raise) is identical across every adapter and the parametrization itself *is* the point per `14-directory-structure.md`.

## Dependency rules
- Depends on every adapter in `classical/` and `pqc/`.

## Source docs
`14-directory-structure.md`, `04-functional-requirements.md`
