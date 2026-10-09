# `pyproject.toml`

**Location:** `packages/quantx-core/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-core`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-core`.
- **Depends on:** Nothing internal to QuantX — the foundation.
- **Third-party runtime dependencies:** No required third-party runtime dependency for the interfaces themselves; `redis_kv_store.py` gates its `redis` dependency behind an optional extra.
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
