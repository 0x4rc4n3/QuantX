# `rate_limit_headers.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Attaches `Retry-After` and related rate-limit headers to responses when a `RateLimiter` gate has tripped, so sidecar clients get standard, machine-readable backoff guidance rather than having to parse the error body.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/middleware/`
- **Depends on:** `quantx_core.exceptions.rate_limited_error.RateLimitedError` (Layer 0, to detect when this applies)
- **Imported by:** `main.py` (installed as ASGI middleware)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `RateLimitedError` (Layer 0)
- **Implements:** ASGI middleware attaching `Retry-After` (and related) headers on a `429` response.
- **Outside:** The rate-limiting decision itself — that's the library's `RateLimiter` instances, this middleware only annotates the resulting response.
- **Inside:** Header attachment on `429` responses.
- **Security notes:** None beyond ensuring rate-limit information is surfaced consistently, per `08-api-specification.md`.

## Required behavior
- When a request results in a `429 rate_limited` response, attaches a `Retry-After` header with guidance on when to retry.

## Inputs / outputs
- **In:** a `429` response from the error-mapping layer.
- **Out:** the same response, with `Retry-After` (and related) headers attached.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised indirectly via router tests that trigger rate limiting.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- The rate-limiting decision itself.

## Source docs
`08-api-specification.md`
