# `quantx-wallet/tests/security/`

## What this is
Layer 6-7's security suite: SR-9 (vault metadata AAD), vault-corruption handling, SR-6 (backend unavailability), and SR-11 (backup-code half).

## Part of
`quantx-wallet`, Layers 6-7.

## Contains
- `test_sr_09_vault_metadata_aad_authenticated.py` — SR-9
- `test_vault_corruption_raises_not_silent_empty.py` — FR-6.3, foundational, no single SR number
- `test_sr_06_backend_unavailable_raises_explicit_error.py` — SR-6
- `test_sr_11_backup_code_replay_rejected.py` — SR-11 (backup-code half; the push-approval half lives in `quantx-authenticator`)

## Why divided this way
Named `test_sr_<NN>_*` where a single numbered item applies, descriptively named where the requirement (FR-6.3) is foundational rather than tied to one SR ID, per `14-directory-structure.md`'s convention and its exception.

## Dependency rules
- SR-9/corruption tests depend on `encrypted_file_backend.py`.
- SR-6 test depends on `os_keychain_backend.py`/`hsm_pkcs11_backend.py`.
- SR-11 test depends on `backup_code_manager.py`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
