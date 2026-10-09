# `quantx_wallet` — package source root

## What this is
Layers 6-7: key custody (`KeyWallet` + `backends/`) and recovery (`backup_code_manager.py`, `device_linker.py`), plus the vault-metadata value type shared across custody backends.

## Part of
`quantx-wallet`, Layers 6-7.

## Contains
- `key_wallet.py` — public class, delegates to a backend, no storage logic itself
- `vault_metadata.py` — value type, included in AEAD AAD
- `backup_code_manager.py` — exactly-once code verification
- `device_linker.py` — non-replayable device-pairing tokens
- `backends/` — the three swappable custody backends

## Why divided this way
Custody (Layer 6) and recovery (Layer 7) are treated as one package per `14-directory-structure.md` (the layer table itself already treats 6-7 as one unit), but each concern still gets its own file.

## Dependency rules
- `key_wallet.py` depends only on `backends/wallet_backend_interface.py` (P1) — never a concrete backend directly.
- `backup_code_manager.py`/`device_linker.py` depend on Layer-0 `ReplayStore`/`KeyValueStore` directly, not on `key_wallet.py` — recovery credentials (codes, pairing tokens) are replay-tracked independently of key-material storage.

## Source docs
`06-system-architecture.md`, `14-directory-structure.md`, `04-functional-requirements.md`
