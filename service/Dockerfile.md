# `Dockerfile`

**Location:** `service/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Container build for the optional REST sidecar deployment.

## Required contents / behavior
- Multi-stage build: install `service/`'s dependencies (including whichever `packages/quantx-*` libraries it needs) and run under Uvicorn/Gunicorn (`06-system-architecture.md`).
- Never bakes secret material (signing keys, backend credentials) into the image layer — those come from environment/secret manager at runtime (`10-security-requirements.md`).

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`06-system-architecture.md`, `10-security-requirements.md`
