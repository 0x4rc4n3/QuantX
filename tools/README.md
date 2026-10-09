# `tools/` — dev/CI helpers

## What this is
Scripts and lint checks that support development and CI but are never shipped as part of any publishable package (`14-directory-structure.md`).

## Part of
Top-level, alongside `packages/` and `service/`.

## Contains
- `softhsm2/` — provisions the SoftHSM2 dev token `hsm_pkcs11_backend.py` tests against
- `fuzzing/` — runs both mandatory wire-parser fuzz suites together
- `lint/` — three custom CI lint checks enforcing architectural rules that a type checker alone can't catch

## Why divided this way
Three unrelated categories of dev/CI tooling, kept separate from any package's `src/` so they're never accidentally packaged/shipped.

## Dependency rules
- Nothing under `packages/` or `service/` imports anything from `tools/` — the dependency direction is one-way (CI/dev calls into `tools/`, never the reverse).

## Source docs
`14-directory-structure.md`, `02-build-order.md`
