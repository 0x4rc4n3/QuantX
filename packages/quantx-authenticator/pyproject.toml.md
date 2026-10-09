# `pyproject.toml`

**Location:** `packages/quantx-authenticator/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Package metadata and dependency declaration for `quantx-authenticator`, independently publishable per `01-product-requirements.md`.

## Required contents / behavior
- Package name: `quantx-authenticator`.
- **Depends on:** `quantx-core` (Layer 0); `quantx-wallet` (Layer 6, once it exists, for durable secret storage, per D11).
- **Third-party runtime dependencies:** None for OTP. TOTP and HOTP are built on the standard library `hmac` and checked against the RFC 4226 and RFC 6238 test vectors (D-015).
- Declares no dependency on anything above its own layer, and no dependency on `service/` (the sidecar depends on packages, never the reverse).

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`
