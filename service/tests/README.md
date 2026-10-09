# `service` — `tests/`

## What this is
The sidecar's test suite: one file per router, plus the sidecar-boundary SR-1 security test.

## Part of
`service`, the REST sidecar.

## Contains
- `conftest.py` — a FastAPI test client wired via `wiring.py` against Recipe-A-style in-memory backends
- `routers/` — one test file per router
- `security/` — the sidecar-boundary SR-1 test

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- All router tests share the same test-client fixture from `conftest.py`.

## Source docs
`14-directory-structure.md`, `08-api-specification.md`
