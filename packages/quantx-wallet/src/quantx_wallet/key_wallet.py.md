# `key_wallet.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The public `KeyWallet` class — delegates actual storage to a backend implementing `wallet_backend_interface.py`'s shared Protocol. Contains no storage logic itself (FR-6.1).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet`
- **Depends on:** `backends/wallet_backend_interface.py` (this package, the Protocol every backend implements)
- **Imported by:** `totp_provider.py`/`hotp_provider.py` (Layer 5, once Layer 6 exists, per D11); `backup_code_manager.py`, `device_linker.py` (this package)

## Docstring contract
- **Layer:** 6
- **Depends on:** The wallet backend `Protocol` (this package)
- **Implements:** `store(key_id, key_material) -> None`; `retrieve(key_id) -> bytes`
- **Outside:** Any actual storage mechanism — that's entirely the wired backend's job.
- **Inside:** Delegation only — validating inputs, forwarding to the backend, translating backend errors where needed.
- **Security notes:** FR-6.1: contains no storage logic itself — a security property in its own right, since it means swapping custody backend (file → keychain → HSM) changes zero lines in this file.

## Required behavior
- Delegates actual storage to a backend implementing `wallet_backend_interface.py`'s shared Protocol — the wallet itself contains no storage logic (FR-6.1).
- Constructor takes a backend instance (P1) — never constructs a concrete backend itself.
- Propagates backend-raised errors (`BackendUnavailableError`) rather than catching and masking them (SR-6).

## Inputs / outputs
- **In:** `store`: `key_id`, `key_material`. `retrieve`: `key_id`.
- **Out:** `store`: none (or confirmation). `retrieve`: `key_material`, or a propagated backend error.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Corruption of vault contents raises an explicit error — never silently returns an empty result (FR-6.3, `13-error-and-edge-cases.md`) — enforced by the backend, propagated unchanged through this class.

## Security notes
- **FR-6.1.** No storage logic of its own — pure delegation, so a custody-backend swap is a constructor argument, never a rewrite (`01-product-requirements.md`'s core value proposition).

## Mandatory tests this must pass
- `tests/test_key_wallet.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Any specific backend's storage mechanics — `backends/`.

## Key format and residency (D-007, D-008)
- Software custody (dev and staging) stores seeds with an AAD-authenticated `key_format` tag; accepted values are in D-007. In production, keys are HSM or KMS resident (D-008): there are no key bytes to store, and `retrieve` raises `KeyNotExportableError`.

## Source docs
`04-functional-requirements.md`, `01-product-requirements.md`, `13-error-and-edge-cases.md`
