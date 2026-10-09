# `gcp_kms_backend.py`

**Package:** `quantx-wallet` · **Layer:** 6 · **Status:** pre-implementation spec for a file that does not exist yet.

## Purpose
Custody backend for Google Cloud KMS (D-008). Private keys are generated and used inside the service; this backend returns `Signer` and decapsulator handles bound to a key reference and never returns key bytes.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet/backends/`
- **Depends on:** `wallet_backend_interface.py`, `quantx_core` interfaces; the provider's client library as the only third-party dependency
- **Imported by:** `key_wallet.py`, `quantx_service/wiring.py`

## Docstring contract
- **Layer:** 6
- **Implements:** the resident-key backend methods in `wallet_backend_interface.py`
- **Outside:** Algorithm choice (registry), message construction (D-009)
- **Inside:** Calls to Google Cloud KMS, error mapping, capability probe
- **Security notes:** Credentials come from the platform identity, never from config (CFG-4). No key bytes in memory, logs or errors.

## Required behavior
- ML-DSA signing keys; ML-KEM only where the provider offers it, and it is reported as preview (W11).
- A capability probe at construction; an unsupported algorithm raises `BackendUnavailableError`, never a failed verification.
- Signing payload size is checked against the service limit and fails closed.
- Network and service errors map to typed errors; nothing is retried in a way that could sign twice with a different payload.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Throttling or outage: fail closed, no fallback to software custody.
- Key disabled or deleted: raise a typed error and issue no token.

## Mandatory tests this must pass
- `tests/backends/test_gcp_kms_backend.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always. **P6.** No docstring claims a capability the code doesn't have: do not call this on-token PQC unless the provider reports it.

## Explicitly out of scope for this file
- Software custody, other providers.

## Source docs
- `DECISIONS.md` (D-008, D-009), `10-security-requirements.md` SR-6
