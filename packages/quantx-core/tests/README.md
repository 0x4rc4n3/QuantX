# `quantx-core` — `tests/`

## What this is
The test suite for Layer 0 — every `interfaces/` Protocol's concrete implementations and the SR items enforced at this layer (SR-3, SR-4, SR-14).

## Part of
`quantx-core`, Layer 0.

## Contains
- `conftest.py` — shared fixtures (a fake `Clock`, a fresh `InMemoryKVStore`, etc.)
- `impls/` — one test file per `impls/` implementation, mirroring `src/quantx_core/impls/`
- `security/` — the SR-3, SR-4, and SR-14 enforcement tests for this package

## Why divided this way
Mirrors `src/` folder-for-folder per `14-directory-structure.md`'s ground rules, plus a `security/` subfolder for anything verifying an SR item.

## Dependency rules
- `impls/` tests depend only on the one implementation file they test, plus shared `conftest.py` fixtures.
- `security/` tests may exercise more than one impl together where an SR item's failure mode spans them (e.g. clock-injection discipline across every timestamp-consuming impl in this package).

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
