# `quantx-zkp` — Layer 9 — Anonymous membership proofs

## What this is
Layer 9: real, working Merkle-tree group-membership proofs (honestly scoped as non-anonymous), plus the deliberately-unimplemented placeholder for true anonymous proofs pending a funded, scoped external audit (D9). One or more components in this package are `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`) — see each gated file's own notice and `docs/adr/`.

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
Yes, as `quantx-zkp` on PyPI (or a private index), per `01-product-requirements.md`.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
