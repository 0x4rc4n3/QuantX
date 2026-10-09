# `os_keychain_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-6).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/key_wallet_backends.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Real OS-keychain-backed key custody — a genuine integration with the host OS's keychain service, or an explicit typed error if unavailable in the current environment. Never a silent fallback to weaker behavior (FR-6.5, SR-6).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet/backends/`
- **Depends on:** `wallet_backend_interface.py` (this package); `quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError` (Layer 0)
- **Imported by:** `key_wallet.py` (constructor-wired for Recipe B)

## Docstring contract
- **Layer:** 6
- **Depends on:** `wallet_backend_interface.Protocol` (this package); `BackendUnavailableError` (Layer 0)
- **Implements:** `store`/`retrieve` per `wallet_backend_interface.py`, against the host OS keychain
- **Outside:** File-based or HSM-based storage — other backend files.
- **Inside:** OS-keychain API integration, and explicit failure signaling when unavailable.
- **Security notes:** SR-6 in full: real integration or explicit typed error, never a silent in-memory-dict fallback.

## Required behavior
- Built as a real integration with the host OS's keychain service — either works for real or raises `NotImplementedError`/`BackendUnavailableError` explicitly (FR-6.5).
- Never silently behaves like an in-memory dict while claiming to be keychain-backed (SR-6).

## Inputs / outputs
- **In:** `store`: `key_id`, `key_material`, `VaultMetadata`. `retrieve`: `key_id`.
- **Out:** `store`/`retrieve` against the real OS keychain, or an explicit raised error if the keychain service isn't available in the current environment.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `OSKeychainBackend` is requested but not actually available/integrated in the current environment → raises `NotImplementedError`/`BackendUnavailableError` explicitly — never silently behaves like an in-memory dict (SR-6, `13-error-and-edge-cases.md`).

## Security notes
- **SR-6.** Real integration or explicit typed error — never a silent fallback to weaker storage.
- This is a `GATE_REVIEW_REQUIRED` component.

## Mandatory tests this must pass
- `tests/backends/test_os_keychain_backend.py`
- `tests/security/test_sr_06_backend_unavailable_raises_explicit_error.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- File-based or HSM-based storage — other backend files.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
