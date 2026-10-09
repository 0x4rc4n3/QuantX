# `vault_metadata.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The vault-metadata value type (algorithm, `created_at`, rotation_state) that `encrypted_file_backend.py` includes in its AES-GCM AAD, so metadata tampering is detected, not just payload tampering (FR-6.2, SR-9).

## Part of
- **Depends on:** `quantx_core.interfaces.clock.Clock` (Layer 0, for `created_at`)
- **Imported by:** `backends/encrypted_file_backend.py` (this package)

## Shape
- `key_id` — key.
- `algorithm` — which algorithm this key material is for.
- `created_at` — from injected `Clock`.
- `rotation_state` — the key's rotation status The value set is unresolved: `07-database-design.md` names the field but does not enumerate its values, so it must be accepted in `docs/DECISIONS.md` before this file is implemented.
- Immutable — a vault entry's metadata, once written, is authenticated inside the AEAD AAD (SR-9); this type itself doesn't support in-place mutation of a stored entry's metadata.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Vault metadata is tampered with but payload ciphertext is untouched → detected — metadata is inside the AEAD AAD, not stored unauthenticated alongside it (`13-error-and-edge-cases.md`).

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Key format and residency (D-007, D-008)
- Software custody (dev and staging) stores seeds with an AAD-authenticated `key_format` tag; accepted values are in D-007. In production, keys are HSM or KMS resident (D-008): there are no key bytes to store, and `retrieve` raises `KeyNotExportableError`.

## Source docs
`07-database-design.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
