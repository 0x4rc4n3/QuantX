# `quantx-authenticator` — `tests/`

## What this is
The test suite for Layer 5: one file per provider, plus the independent-rate-limiter, SR-5, and SR-11 security tests.

## Part of
`quantx-authenticator`, Layer 5.

## Contains
- `conftest.py`
- `test_totp_provider.py`, `test_hotp_provider.py`, `test_push_authenticator.py`
- `security/` — independent rate-limiter check, SR-5, SR-11

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- Each test file depends on the one provider it names, plus shared fixtures with test-fixture TOTP/HOTP secrets (per D11, real `KeyWallet`-backed storage is Layer 6's test surface, not this package's).

## Source docs
`14-directory-structure.md`, `00-index.md`
