# `hsm_pkcs11_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-6).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/key_wallet_backends.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Real PKCS#11-based HSM key custody, built against **SoftHSM2** as the development/test target so this backend gets built for real, on the same timeline as everything else, without waiting for client-specific hardware (`02-build-order.md`'s named real blocker and its own stated resolution).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet/backends/`
- **Depends on:** `wallet_backend_interface.py` (this package); A PKCS#11 Python binding, against `tools/softhsm2/setup_softhsm2_dev_token.sh`'s provisioned dev token; `quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError` (Layer 0)
- **Imported by:** `key_wallet.py` (constructor-wired for Recipe B, with a client's real HSM substituted for SoftHSM2 as a configuration change, not new code)

## Docstring contract
- **Layer:** 6
- **Depends on:** `wallet_backend_interface.Protocol` (this package); a PKCS#11 binding; `BackendUnavailableError` (Layer 0)
- **Implements:** `store`/`retrieve` per `wallet_backend_interface.py`, against a PKCS#11 module
- **Outside:** File-based or OS-keychain storage — other backend files.
- **Inside:** PKCS#11 session/slot handling against SoftHSM2 (dev/test) or a client's real HSM (production, same code path).
- **Security notes:** SR-6 in full — this is the one backend whose "real integration" bar is explicitly unblocked by SoftHSM2 rather than waiting on client hardware.

## Required behavior
- Built as a real PKCS#11 integration against SoftHSM2 as the dev/test target — not held back for client-specific hardware (`02-build-order.md`'s Real (non-arbitrary) blockers section: "Don't wait for client-specific hardware — install SoftHSM2 ... immediately").
- Either works for real against the configured PKCS#11 module or raises `NotImplementedError`/`BackendUnavailableError` explicitly (FR-6.5, SR-6).
- Swapping in a client's real HSM later is a configuration change (which PKCS#11 module/slot is pointed at), not new code (`02-build-order.md`).

## Inputs / outputs
- **In:** `store`: `key_id`, `key_material`, `VaultMetadata`. `retrieve`: `key_id`.
- **Out:** `store`/`retrieve` against the configured PKCS#11 module (SoftHSM2 in dev, a real HSM in production), or an explicit raised error if the module is unreachable.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `HsmPkcs11Backend` is requested but not actually available/integrated in the current environment → raises `NotImplementedError`/`BackendUnavailableError` explicitly — never silently behaves like an in-memory dict (SR-6, `13-error-and-edge-cases.md`).

## Security notes
- **SR-6.** Real integration or explicit typed error.
- This is a `GATE_REVIEW_REQUIRED` component.

## Mandatory tests this must pass
- `tests/backends/test_hsm_pkcs11_backend.py` — runs against the SoftHSM2 dev token from `tools/softhsm2/`
- `tests/security/test_sr_06_backend_unavailable_raises_explicit_error.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- File-based or OS-keychain storage — other backend files.
- Provisioning the SoftHSM2 dev token itself — `tools/softhsm2/setup_softhsm2_dev_token.sh`.

## Key residency (D-008)
- Keys are generated inside the token and never leave it. The backend implements `generate(key_id, algorithm) -> public_key_bytes`, `signer_for(key_id) -> Signer` and `decapsulator_for(key_id)`; `retrieve` raises `KeyNotExportableError`.
- PQC mechanisms are used only if the module advertises PKCS#11 3.x PQC support; otherwise construction raises `BackendUnavailableError` (SR-6). Released SoftHSM2 has none, so PQC tests need SoftHSMv3, kryoptic or a vendor test HSM (availability to verify). SoftHSM2 still covers classical keys and AES.
- Signing payloads follow D-009; a payload over the module's size limit fails closed.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `02-build-order.md`, `13-error-and-edge-cases.md`
