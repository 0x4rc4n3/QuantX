# `exceptions/` — Layer-0 typed exceptions

## What this is
The typed exception vocabulary shared across the whole codebase, so that failure modes are distinguishable by type rather than by string-matching a generic exception's message.

## Part of
`quantx-core`, Layer 0.

## Contains
- `backend_unavailable_error.py` — `BackendUnavailableError` (SR-4, SR-6)
- `replay_detected_error.py` — `ReplayDetectedError` (SR-11, FR-4.2)
- `rate_limited_error.py` — `RateLimitedError` (FR-4.4, FR-5.2, SR-5)
- `malformed_input_error.py` — `MalformedInputError` (FR-0.1, mandatory wire-parser fuzz tests)

## Why divided this way
One exception type per file per `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- Depends on nothing else in QuantX beyond the standard exception hierarchy.
- Imported by any component that raises or catches these — including, at the REST-sidecar boundary, the `service/src/quantx_service/errors/` files that map each one onto an HTTP status code (`08-api-specification.md`'s error model).

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`, `08-api-specification.md`
