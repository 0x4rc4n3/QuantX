# `quantx-authenticator` — Layer 5 — Second factor

## What this is
Layer 5: TOTP, HOTP, and push-notification second factors — each an additional required gate in `SessionOrchestrator`, never a replacement for the primary factor.

## Part of
One of the ten layered packages under `packages/` (`01-product-requirements.md`, `06-system-architecture.md`).

## Contains
- `pyproject.toml` — package metadata and dependencies
- `src/` — the package's importable source
- `tests/` — this package's test suite, including `tests/security/` where applicable

## Why divided this way
Independently publishable per `01-product-requirements.md`'s "shipped as independently-publishable Python packages" — a consumer who only needs this layer and below never pulls in anything above it.

## Dependency rules
- **Depends on:** `quantx-core` (Layer 0); `quantx-wallet` (Layer 6, once it exists, for durable secret storage, per D11).
- Never imports sideways (another package at the same layer) or upward (a higher-numbered layer).

## Independently publishable?
Yes, as `quantx-authenticator` on PyPI (or a private index), per `01-product-requirements.md`.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
