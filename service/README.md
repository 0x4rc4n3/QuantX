# `service` — optional REST sidecar

## What this is
A FastAPI-based REST sidecar wrapping the `packages/quantx-*` libraries for consumers who want an HTTP API instead of (or alongside) a direct Python dependency — challenge issuance, verification, and session validation over HTTP, per `08-api-specification.md`.

## Part of
Top-level, alongside `packages/` — **not** itself one of the ten layered packages (`14-directory-structure.md`).

## Contains
- `pyproject.toml` — sidecar-only dependencies (FastAPI, Uvicorn/Gunicorn)
- `Dockerfile` — container build for sidecar deployment
- `src/quantx_service/` — application code
- `tests/` — router tests and the sidecar-boundary SR-1 test

## Why divided this way
Kept top-level and explicitly separate from `packages/` so that installing any layered library package never pulls in FastAPI/Uvicorn as a transitive dependency — the sidecar is optional, the libraries are not (`01-product-requirements.md`, `14-directory-structure.md`).

## Dependency rules
- Depends on `packages/quantx-*` libraries as an ordinary consumer.
- No file under `packages/` may import anything from `service/` — the dependency direction is one-way.

## Independently publishable?
Yes, as `quantx-service` — but it's explicitly optional; nothing else in the repo depends on it existing (`01-product-requirements.md`'s "packages plus an optional REST sidecar" framing).

## Source docs
`14-directory-structure.md`, `08-api-specification.md`, `01-product-requirements.md`
