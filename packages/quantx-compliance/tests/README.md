# `quantx-compliance` — `tests/`

## What this is
The test suite for Layer 10: the data model, both scanners, the standards catalog, the report generator, and the SR-13/SR-15 security tests.

## Part of
`quantx-compliance`, Layer 10.

## Contains
- `conftest.py`
- `test_crypto_bom_model.py`
- `scanners/` — one test file per scanner
- `test_standards_catalog.py`, `test_compliance_report_generator.py`
- `security/` — SR-13, SR-15

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- Each test file depends on the one `src/` file/folder it names plus shared fixtures.

## Source docs
`14-directory-structure.md`
