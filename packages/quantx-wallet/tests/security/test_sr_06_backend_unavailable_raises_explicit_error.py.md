# `test_sr_06_backend_unavailable_raises_explicit_error.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `OSKeychainBackend` and `HsmPkcs11Backend` raise explicit typed errors when unavailable, rather than silently behaving like an in-memory dict.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/security/`
- **Depends on:** `os_keychain_backend.py`; `hsm_pkcs11_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** Both custody backends.
- **Implements:** The mandatory automated security test for SR-6.
- **Outside:** `EncryptedFileBackend`'s SR-9 scenario — separate file.
- **Inside:** Simulated backend unavailability.
- **Security notes:** This file **is** the SR-6 enforcement check.

## Required behavior
- Simulate the OS keychain service being unavailable (test environment without one, or a fault injection) → confirm `OSKeychainBackend` raises `BackendUnavailableError`/`NotImplementedError` explicitly, never silently returns success.
- Simulate the PKCS#11 module being unreachable → confirm `HsmPkcs11Backend` does the same.

## Inputs / outputs
- **In:** simulated backend unavailability.
- **Out:** must raise explicitly, never degrade silently.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `HsmPkcs11Backend` or `OSKeychainBackend` is requested but not actually available/integrated in the current environment → raises `NotImplementedError`/`BackendUnavailableError` explicitly (SR-6, `13-error-and-edge-cases.md`).

## Security notes
- **SR-6.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-6 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- `EncryptedFileBackend`'s SR-9 scenario — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
