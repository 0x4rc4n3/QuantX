# `quantx-crypto-adapters` — Layer 1 — Algorithm adapters

## What this is
Layer 1: one file per algorithm — three classical and four PQC adapters, all `cryptography`-backed (a fifth PQC adapter, SLH-DSA, is specified but blocked on upstream, D-006), each implementing a Layer-0 interface.

## Part of
One of the ten layered packages under `packages/` (`01-product-requirements.md`, `06-system-architecture.md`).

## Contains
- `pyproject.toml` — package metadata and dependencies
- `src/` — the package's importable source
- `tests/` — this package's test suite, including `tests/security/` where applicable

## Why divided this way
Independently publishable per `01-product-requirements.md`'s "shipped as independently-publishable Python packages" — a consumer who only needs this layer and below never pulls in anything above it.

## Dependency rules
- **Depends on:** `quantx-core` (Layer 0).
- Never imports sideways (another package at the same layer) or upward (a higher-numbered layer).

## Independently publishable?
Yes, as `quantx-crypto-adapters` on PyPI (or a private index), per `01-product-requirements.md`.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
