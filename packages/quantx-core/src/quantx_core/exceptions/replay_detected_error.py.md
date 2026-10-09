# `replay_detected_error.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The explicit error raised when `ReplayStore.consume_once()` detects a token that has already been consumed.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/exceptions/`
- **Depends on:** Python's built-in `Exception`.
- **Imported by:** `in_memory_replay_store.py` (Layer 0 impl); `session_orchestrator.py`, `challenge_issuer.py` (Layer 4); `push_authenticator.py` (Layer 5), `backup_code_manager.py` (Layer 6-7); `service/src/quantx_service/errors/already_consumed_error.py` maps this to the sidecar's `409 already_consumed` response

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal beyond the standard exception hierarchy.
- **Implements:** `ReplayDetectedError(Exception)` — a typed exception, no custom behavior beyond carrying a message and (where noted) structured context.
- **Outside:** Deciding when to raise it — that's every raising component's own concern.
- **Inside:** The exception type itself and its constructor shape.
- **Security notes:** **SR-11 / FR-4.2.** This is the concrete signal a caller gets when a challenge, session token, backup code, or push approval is replayed — consume-once semantics apply uniformly regardless of which of those four credential types triggered it.

## Required behavior
- `ReplayDetectedError` is a distinct, typed exception — never conflated with a generic `Exception` or `ValueError`, so callers (including the REST sidecar's error-mapping layer) can catch it specifically.
- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)`.

## Inputs / outputs
- **In:** a human-readable message and any structured context the raising site provides.
- **Out:** nothing — it's raised, not returned.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-11 / FR-4.2.** This is the concrete signal a caller gets when a challenge, session token, backup code, or push approval is replayed — consume-once semantics apply uniformly regardless of which of those four credential types triggered it.

## Mandatory tests this must pass
- Exercised indirectly by every test that asserts a specific failure mode raises this exception rather than a generic one or silently passing.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Deciding when to raise this — that's each raising component's own file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
