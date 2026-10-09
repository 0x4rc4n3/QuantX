# `quantx-crypto-adapters` — `tests/`

## What this is
One test file per adapter, mirroring `src/quantx_crypto_adapters/` folder-for-folder, plus the shared fail-closed-on-malformed-input security test parametrized across every adapter.

## Part of
`quantx-crypto-adapters`, Layer 1.

## Contains
- `conftest.py` — shared fixtures (keypair generation helpers per algorithm)
- `classical/` — one test file per classical adapter
- `pqc/` — one test file per PQC adapter
- `security/` — the shared fail-closed test, parametrized across every adapter (FR-0.1)

## Why divided this way
Mirrors `src/` folder-for-folder per `14-directory-structure.md`'s ground rules.

## Dependency rules
- Each test file depends only on the one adapter it tests, plus shared `conftest.py` fixtures.

## Source docs
`14-directory-structure.md`, `02-build-order.md`
