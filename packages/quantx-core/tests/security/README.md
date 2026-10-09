# `quantx-core/tests/security/`

## What this is
The SR-item enforcement tests owned by Layer 0: SR-3 (in-memory cap), SR-4 (redis failure handling), and SR-14 (clock injection discipline).

## Part of
`quantx-core`, Layer 0.

## Contains
- `test_sr_03_in_memory_max_entries_cap.py` — SR-3
- `test_sr_04_redis_backend_failure_handling.py` — SR-4
- `test_sr_14_clock_never_defaults.py` — SR-14

## Why divided this way
One file per SR item, named `test_sr_<NN>_<slug>.py`, per `14-directory-structure.md`'s naming convention.

## Dependency rules
- Each depends only on the specific impl(s) its SR item concerns.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
