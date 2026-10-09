# `pyproject.toml`

**Location:** `packages/quantx-session/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-session`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-session`.
- **Depends on:** `quantx-core` (Layer 0), `quantx-combiners`/`quantx-registry` (Layers 2-3, via `AlgorithmRegistry`).
- **Third-party runtime dependencies:** None beyond `quantx-core`/`quantx-combiners`/`quantx-registry`.
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
