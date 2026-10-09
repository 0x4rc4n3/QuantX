# `wallet_backend_interface.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The shared `Protocol` every `KeyWallet` backend implements — the contract that makes swapping `EncryptedFileBackend` for `OSKeychainBackend`/`HsmPkcs11Backend` a constructor argument, never a rewrite (FR-6.1).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet/backends/`
- **Depends on:** Nothing — a Layer-6 foundational Protocol for this package.
- **Imported by:** `encrypted_file_backend.py`, `os_keychain_backend.py`, `hsm_pkcs11_backend.py` (each implements it); `key_wallet.py` (type-hints its constructor against this interface, per P1)

## Docstring contract
- **Layer:** 6
- **Depends on:** Nothing internal.
- **Implements:** `store(key_id, key_material, metadata) -> None`; `retrieve(key_id) -> (key_material, metadata)`
- **Outside:** Any concrete storage mechanism.
- **Inside:** The method shape every backend must satisfy.
- **Security notes:** FR-6.5: every implementing backend either really works or raises `NotImplementedError`/`BackendUnavailableError` — never silently behaves like an in-memory dict while claiming otherwise (SR-6).

## Required behavior
- **Resident-key backends (D-008)** add `generate(key_id, algorithm) -> public_key_bytes`, `signer_for(key_id) -> Signer` and `decapsulator_for(key_id)`. For keys that stay inside an HSM or KMS, `retrieve` raises `KeyNotExportableError` and never returns key bytes.
- A `typing.Protocol` defining `store`/`retrieve` including vault metadata, so every backend handles metadata the same way (feeding into SR-9's AAD-authentication requirement wherever the backend's own encryption scheme supports it).
- No default/concrete logic — contract only.

## Inputs / outputs
- **In/Out:** per-method, defined by the Protocol.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-6.5 / SR-6.** Every concrete backend either really works or raises an explicit typed error — this Protocol's shape is what makes that consistent across all three backends.

## Mandatory tests this must pass
- No dedicated test file — conformance is exercised by each backend's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live alongside this file.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`
