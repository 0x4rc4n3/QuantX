# `quantx_session` — package source root

## What this is
Layer 4: challenge issuance and the session orchestrator, plus the Recipe-A wiring helper that makes the whole system demoable end-to-end for the first time.

## Part of
`quantx-session`, Layer 4.

## Contains
- `challenge_issuer.py` — issues challenges via `KeyValueStore`
- `challenge_record.py` — `Challenge` value type
- `session_orchestrator.py` — gates all factors, mints tokens last (SR-10)
- `session_token.py` — `SessionToken` value type
- `default_setup.py` — Recipe-A wiring helper

## Why divided this way
Orchestration logic, its two value types, and the convenience wiring helper are each independently reviewable/testable per `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- Depends on Layer 2 (combiners, via Layer 3's `AlgorithmRegistry`) and Layer 0 directly — never imports a Layer-1 adapter directly (FR-X.2).
- `default_setup.py` is the only file in this package that constructs Layer 0 reference impls directly — `challenge_issuer.py`/`session_orchestrator.py` take everything via constructor injection (P1).

## Source docs
`06-system-architecture.md`, `02-build-order.md`, `14-directory-structure.md`
