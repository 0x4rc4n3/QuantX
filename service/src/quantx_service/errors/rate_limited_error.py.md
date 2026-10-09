# `rate_limited_error.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Maps A `RateLimiter` instance has tripped (maps Layer 0's `RateLimitedError`); includes a `Retry-After` header. onto the sidecar's `429 rate_limited` response, using `error_envelope.py`'s shape.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/errors/`
- **Depends on:** `error_envelope.py` (this package); The corresponding Layer-0/library exception this file maps, where one exists
- **Imported by:** `routers/*.py`, via FastAPI exception handlers

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `error_envelope.py`; the mapped library exception, where applicable
- **Implements:** A FastAPI exception handler mapping the relevant library exception (or validation failure) to `429 rate_limited`.
- **Outside:** Any other error kind — one file per error kind, per `14-directory-structure.md`.
- **Inside:** The `429`/`rate_limited` mapping and `error_envelope.py` shaping.
- **Security notes:** Ensures the specific failure reason is surfaced accurately rather than collapsed into a generic 500, per `08-api-specification.md`'s error model.

## Required behavior
- Maps A `RateLimiter` instance has tripped (maps Layer 0's `RateLimitedError`); includes a `Retry-After` header to `429 rate_limited`, shaped via `error_envelope.py`.
- Never lets the underlying library exception's raw message/traceback leak to the client beyond what `error_envelope.py`'s `message`/`details` fields are meant to carry.

## Inputs / outputs
- **In:** the mapped library exception or validation failure.
- **Out:** an HTTP `429` response with `error_code: "rate_limited"`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- Surfaces `429 rate_limited` accurately rather than a generic 500, per `08-api-specification.md`'s error model — A `RateLimiter` instance has tripped (maps Layer 0's `RateLimitedError`); includes a `Retry-After` header

## Mandatory tests this must pass
- Exercised indirectly via router tests that trigger this specific failure mode.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Every other error kind — separate files.

## Source docs
`08-api-specification.md`
