# `service/tests/security/`

## What this is
The sidecar's one dedicated security test: the sidecar never trusts a client-declared mode (SR-1's boundary-layer instance).

## Part of
`service`, the REST sidecar.

## Contains
- `test_sr_01_sidecar_never_trusts_declared_mode.py`

## Why divided this way
Named `test_sr_<NN>_*` per `14-directory-structure.md`'s convention.

## Dependency rules
- Depends on `verify_router.py` and, transitively, `signature_mode_enforcement.py` (Layer 2).

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
