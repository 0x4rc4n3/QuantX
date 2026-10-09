# `softhsm2/` — SoftHSM2 dev-token provisioning

## What this is
The script that provisions a SoftHSM2 dev token so `hsm_pkcs11_backend.py`'s tests run against a real PKCS#11 module without needing client-specific hardware.

## Part of
`tools/`.

## Contains
- `setup_softhsm2_dev_token.sh` — provisions the dev token

## Why divided this way
Kept separate from `quantx-wallet`'s own test suite since it's environment setup, not a test itself, and is a real (non-arbitrary) blocker resolution named explicitly in `02-build-order.md`.

## Dependency rules
- Run once per dev/CI environment setup, before `quantx-wallet`'s `test_hsm_pkcs11_backend.py` can pass.

## Source docs
`02-build-order.md`
