# `quantx-wallet` — `tests/`

## What this is
The test suite for Layers 6-7 — key custody backends (including the SoftHSM2-backed HSM test), the wallet, backup codes, device linking, and the SR-6/SR-9/SR-11 security suite.

## Part of
`quantx-wallet`, Layers 6-7.

## Contains
- `conftest.py`
- `test_key_wallet.py`
- `backends/` — one test file per backend
- `test_backup_code_manager.py`, `test_device_linker.py`
- `security/` — SR-9, vault-corruption, SR-6, SR-11 (backup-code half)

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- `test_hsm_pkcs11_backend.py` runs against the SoftHSM2 dev token provisioned by `tools/softhsm2/setup_softhsm2_dev_token.sh` — it is not a pure in-process unit test.

## Source docs
`14-directory-structure.md`, `02-build-order.md`
