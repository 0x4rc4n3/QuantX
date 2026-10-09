# `error_envelope.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The single, consistent JSON error shape every sidecar error response uses, per `08-api-specification.md`'s error model — so a client can handle failures uniformly regardless of which specific error occurred.

## Part of
- **Depends on:** nothing internal to QuantX (foundational value type).
- **Imported by:** Every file in `errors/`; every router, indirectly, via FastAPI exception handlers

## Shape
- `error_code` — a stable string identifying the error kind (`malformed_request`, `verification_failed`, `not_found`, `already_consumed`, `rate_limited`, `backend_unavailable`).
- `message` — a human-readable explanation.
- `details` — optional structured context specific to the error kind.
- One shape, used consistently by every mapped error in `errors/` — never a bespoke response shape per endpoint.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`08-api-specification.md`
