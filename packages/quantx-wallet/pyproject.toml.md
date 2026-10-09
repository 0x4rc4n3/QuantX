# `pyproject.toml`

**Location:** `packages/quantx-wallet/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-wallet`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-wallet`.
- **Depends on:** `quantx-core` (Layer 0).
- **Third-party runtime dependencies:** `cryptography` (AES-GCM, `encrypted_file_backend.py`); a PKCS#11 binding (`hsm_pkcs11_backend.py`); the host OS's keychain API (`os_keychain_backend.py`).
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
