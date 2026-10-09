# `pyproject.toml`

**Location:** `packages/quantx-crypto-adapters/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-crypto-adapters`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-crypto-adapters`.
- **Depends on:** `quantx-core` (Layer 0).
- **Third-party runtime dependencies:** `cryptography>=48,<51` (all adapters; ML-KEM/ML-DSA need 48+; exact version pinned via lockfile, D6). Requires Python 3.11+ (project floor, `docs/QUANTX-V2-ARCHITECTURE.md` §2; `cryptography` itself supports older versions but that does not lower the project floor, D-010). The upper bound `<51` exists so that each new `cryptography` major is reviewed for PQC API changes before it is allowed (D-010). PQC adapters need a PQC-capable backend: the PyPI wheels bundle OpenSSL >=3.5, but source builds against older OpenSSL/LibreSSL lack ML-KEM/ML-DSA (probed at construction), and from 49.0.0 there are no x86_64 macOS wheels. No `liboqs` dependency (D-006).
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
