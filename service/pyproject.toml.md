# `pyproject.toml`

**Location:** `service/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Declares `quantx-service`'s dependencies (FastAPI, Uvicorn/Gunicorn per `06-system-architecture.md`'s tech-stack table, plus every `packages/quantx-*` library it consumes) and packaging metadata for the optional REST sidecar.

## Required contents / behavior
- Depends on FastAPI and Uvicorn/Gunicorn (`06-system-architecture.md`).
- Depends on whichever `packages/quantx-*` libraries the sidecar wires (at minimum `quantx-core`, `quantx-crypto-adapters`, `quantx-combiners`, `quantx-registry`, `quantx-session`).
- Kept top-level and separate from `packages/` specifically so a library-only consumer never pulls in FastAPI/Uvicorn as a transitive dependency (`14-directory-structure.md`).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`06-system-architecture.md`, `14-directory-structure.md`
