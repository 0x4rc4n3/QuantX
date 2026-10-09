# `quantx_service` — sidecar source root

## What this is
The REST sidecar's application code: entry point, config, composition root, routers, auth, error mapping, and middleware.

## Part of
`service`, the REST sidecar — top-level, not under `packages/` (`14-directory-structure.md`).

## Contains
- `main.py` — FastAPI app assembly
- `config.py` — configuration loading
- `wiring.py` — composition root
- `routers/` — HTTP endpoints
- `auth/` — bearer-token and mTLS client authentication
- `errors/` — the error envelope and one file per error type (`08-api-specification.md`)
- `middleware/` — hybrid-TLS enforcement, rate-limit headers

## Why divided this way
The sidecar is an optional wrapper around the library, not the library itself — `14-directory-structure.md` keeps it top-level, separate from `packages/`, precisely so `pip install quantx-core` never drags in FastAPI/Uvicorn for a library-only consumer.

## Dependency rules
- Depends on the `packages/` libraries (Layers 0-10) as a consumer, never the reverse — no `packages/` file ever imports anything under `service/`.
- Routers depend on `wiring.py`'s constructed objects via dependency injection, never constructing library objects themselves.

## Source docs
`14-directory-structure.md`, `06-system-architecture.md`, `08-api-specification.md`
