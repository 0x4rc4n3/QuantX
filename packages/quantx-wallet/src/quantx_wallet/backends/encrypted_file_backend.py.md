# `encrypted_file_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-9).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/key_wallet_backends.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Encrypted-file-based key custody backend — AES-GCM, with vault metadata included in the AAD so metadata tampering is detected, not just payload tampering (FR-6.2, SR-9). Used by Recipe A/B for key storage.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet/backends/`
- **Depends on:** `wallet_backend_interface.py` (this package); `vault_metadata.py` (this package); `cryptography`'s AES-GCM implementation (D1, no hand-rolled AEAD)
- **Imported by:** `key_wallet.py` (constructor-wired for Recipe A/B)

## Docstring contract
- **Layer:** 6
- **Depends on:** `wallet_backend_interface.Protocol`, `VaultMetadata` (this package); `cryptography`'s AES-GCM
- **Implements:** `store`/`retrieve` per `wallet_backend_interface.py`
- **Outside:** Any other backend's storage mechanism.
- **Inside:** AES-GCM encryption with `VaultMetadata` folded into the AAD, and file-based persistence.
- **Security notes:** SR-9 in full: metadata authenticated in AAD; corruption raises explicitly rather than returning empty.

## Required behavior
- Includes vault metadata in the AES-GCM AAD, so metadata tampering is detected, not just payload tampering (FR-6.2, SR-9).
- Corruption of vault contents raises an explicit error — never silently returns an empty result (FR-6.3).
- Uses `cryptography`'s AES-GCM implementation — never a hand-rolled AEAD (D1).

## Inputs / outputs
- **In:** `store`: `key_id`, `key_material`, `VaultMetadata`. `retrieve`: `key_id`.
- **Out:** `store`: writes an encrypted file. `retrieve`: decrypted `key_material` + `VaultMetadata`, or a raised explicit error on corruption.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Vault file is corrupted → explicit raised error — never a silently-returned empty result (SR-9, `13-error-and-edge-cases.md`).
- Vault metadata is tampered with but payload ciphertext is untouched → detected — metadata is inside the AEAD AAD, not stored unauthenticated alongside it.

## Security notes
- **SR-9.** Vault metadata is included in AEAD AAD; corruption raises explicitly rather than returning empty.
- This is a `GATE_REVIEW_REQUIRED` component (`10-security-requirements.md`'s review-gates list).

## Mandatory tests this must pass
- `tests/backends/test_encrypted_file_backend.py`
- `tests/security/test_sr_09_vault_metadata_aad_authenticated.py`
- `tests/security/test_vault_corruption_raises_not_silent_empty.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- OS-keychain or HSM storage — separate backend files.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `07-database-design.md`
