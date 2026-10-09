# `test_sr_09_vault_metadata_aad_authenticated.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `EncryptedFileBackend` includes vault metadata in the AES-GCM AAD, so metadata tampering is detected even when payload ciphertext is untouched.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/security/`
- **Depends on:** `encrypted_file_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** `encrypted_file_backend.py`
- **Implements:** The mandatory automated security test for SR-9.
- **Outside:** Corruption-handling — separate file.
- **Inside:** Metadata-only tampering detection.
- **Security notes:** This file **is** the SR-9 enforcement check.

## Required behavior
- Store a genuine vault entry, then tamper with only the metadata bytes (leaving payload ciphertext untouched) before `retrieve()`.
- Confirm `retrieve()` fails (AEAD authentication failure), never silently returns the payload with stale/wrong metadata.

## Inputs / outputs
- **In:** a vault entry with tampered metadata.
- **Out:** must fail authentication.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Vault metadata is tampered with but payload ciphertext is untouched → detected (SR-9, `13-error-and-edge-cases.md`).

## Security notes
- **SR-9.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-9 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Corruption-handling — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
