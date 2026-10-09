# `test_gcp_kms_backend.py`

**Package:** `quantx-wallet` · **Status:** pre-implementation test spec.

## What it verifies
- Against recorded or mocked Google Cloud KMS responses: `generate`, `signer_for` and `decapsulator_for` behave per `wallet_backend_interface.py`; `retrieve` raises `KeyNotExportableError`.
- Unsupported algorithms raise `BackendUnavailableError` (E8). Oversized payloads fail closed. Throttling and outages fail closed with no software fallback.
- A real-account smoke test, run only in a labelled integration job, signs a D-009 payload that the software verifier accepts.

## Source docs
- `DECISIONS.md` (D-008, D-009)
