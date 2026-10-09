# `routers/` — HTTP endpoints

## What this is
The three FastAPI routers implementing `08-api-specification.md`'s endpoints: challenge issuance, verification, and session validation.

## Part of
`service`, the REST sidecar.

## Contains
- `challenge_router.py` — `POST /v1/challenges`
- `verify_router.py` — `POST /v1/verify` (SR-1 sidecar-boundary enforcement)
- `session_router.py` — session-token validation

## Why divided this way
One router per resource/endpoint group, the standard FastAPI convention, and consistent with `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- Every router receives its library dependencies via FastAPI dependency injection, sourced from `wiring.py` — no router constructs its own `AlgorithmRegistry`/`SessionOrchestrator`.

## Source docs
`08-api-specification.md`, `14-directory-structure.md`
