# `quantx-threshold` — `tests/`

## What this is
The test suite for Layer 8: policy validation, approval tracking, and the SR-12 duplicate-key security test.

## Part of
`quantx-threshold`, Layer 8.

## Contains
- `conftest.py`
- `test_threshold_policy.py`, `test_threshold_manager.py`
- `security/` — SR-12

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- Each test file depends on the one `src/` file it names plus shared fixtures.

## Source docs
`14-directory-structure.md`
