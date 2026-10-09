# `pyproject.toml`

**Location:** `packages/quantx-compliance/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-compliance`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-compliance`.
- **Depends on:** `quantx-core` (Layer 0, `AlgorithmId` for BOM entries).
- **Third-party runtime dependencies:** `cryptography` (`x509` parsing, `tls_inspector.py` — never `openssl` shell-out, FR-10.3).
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
