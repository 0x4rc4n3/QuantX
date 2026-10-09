# `pyproject.toml`

**Location:** `quantx/ (repo root)` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The repo-root workspace configuration — not a publishable package itself, but the shared tooling config (linting, formatting, test discovery across the monorepo) every `packages/quantx-*` and `service/` package's own `pyproject.toml` builds on top of.

## Required contents / behavior
- Declares this as a monorepo workspace containing the independently-publishable packages under `packages/` plus the optional `service/` sidecar (`01-product-requirements.md`: "independently-publishable Python packages plus an optional REST sidecar").
- Shared dev-tooling configuration (formatter, linter, type checker) referenced by every package's own `pyproject.toml` — never a place where a specific package's runtime dependencies live.
- Does not itself declare `cryptography`, FastAPI, or any other runtime dependency — those are scoped to whichever package actually needs them, per `06-system-architecture.md`'s tech-stack table.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
