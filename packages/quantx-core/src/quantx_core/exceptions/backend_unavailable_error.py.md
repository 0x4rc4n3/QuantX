# `backend_unavailable_error.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The explicit, typed error a storage or custody backend raises when it cannot actually perform its job — never a silent fallback to weaker behavior.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/exceptions/`
- **Depends on:** Python's built-in `Exception`.
- **Imported by:** `redis_kv_store.py` (Layer 0, SR-4 network-failure path); `os_keychain_backend.py`, `hsm_pkcs11_backend.py` (Layer 6-7, SR-6); `service/src/quantx_service/errors/backend_unavailable_error.py` maps this to the sidecar's `503 backend_unavailable` response

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal beyond the standard exception hierarchy.
- **Implements:** `BackendUnavailableError(Exception)` — a typed exception, no custom behavior beyond carrying a message and (where noted) structured context.
- **Outside:** Deciding when to raise it — that's every raising component's own concern.
- **Inside:** The exception type itself and its constructor shape.
- **Security notes:** **SR-4 / SR-6.** A networked `KeyValueStore` backend's connection failure and a custody backend's unavailability are both security-relevant, not just reliability concerns — silently degrading either would be a downgrade, not a UX issue. This exception is how both surface explicitly instead of silently falling back to weaker behavior.

## Required behavior
- `BackendUnavailableError` is a distinct, typed exception — never conflated with a generic `Exception` or `ValueError`, so callers (including the REST sidecar's error-mapping layer) can catch it specifically.
- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)`.

## Inputs / outputs
- **In:** a human-readable message and any structured context the raising site provides.
- **Out:** nothing — it's raised, not returned.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-4 / SR-6.** A networked `KeyValueStore` backend's connection failure and a custody backend's unavailability are both security-relevant, not just reliability concerns — silently degrading either would be a downgrade, not a UX issue. This exception is how both surface explicitly instead of silently falling back to weaker behavior.

## Mandatory tests this must pass
- Exercised indirectly by every test that asserts a specific failure mode raises this exception rather than a generic one or silently passing.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Deciding when to raise this — that's each raising component's own file.

## Source docs
`07-database-design.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
