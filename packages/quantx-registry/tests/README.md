# `quantx-registry` — `tests/`

## What this is
The test suite for Layer 3: role resolution, config loading, config signing, and the unsigned-config-rejection security test.

## Part of
`quantx-registry`, Layer 3.

## Contains
- `conftest.py` — shared fixtures (a real example config, signed and unsigned variants)
- `test_algorithm_registry.py`, `test_registry_role.py`, `test_registry_config_loader.py`, `test_registry_config_signature.py` — one per `src/` file
- `security/` — the unsigned-config-rejection test

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- Each test file depends on the one `src/` file it names, plus shared fixtures.

## Source docs
`14-directory-structure.md`
