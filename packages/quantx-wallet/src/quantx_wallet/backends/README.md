# `backends/` — swappable key-custody backends

## What this is
The shared `Protocol` (`wallet_backend_interface.py`) and its three implementations — encrypted file, OS keychain, HSM/PKCS#11 — that `KeyWallet` delegates to.

## Part of
`quantx-wallet`, Layers 6-7. All three concrete backends are `GATE_REVIEW_REQUIRED`.

## Contains
- `wallet_backend_interface.py` — shared Protocol every backend implements
- `encrypted_file_backend.py` — AES-GCM, metadata in AAD (SR-9)
- `os_keychain_backend.py` — real OS keychain integration or explicit error (SR-6)
- `hsm_pkcs11_backend.py` — real PKCS#11/SoftHSM2 integration or explicit error (SR-6)

## Why divided this way
One backend per file, per `14-directory-structure.md`'s atomicity rule — this is also the literal mechanism behind the architecture's "swap a constructor argument" claim (`01-product-requirements.md`).

## Dependency rules
- Every backend implements `wallet_backend_interface.py`'s Protocol and nothing else in this folder imports another backend (P1).
- None of the three backends is permitted to silently behave like a weaker backend on failure — each either really works or raises an explicit typed error (FR-6.5, SR-6).

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `14-directory-structure.md`
