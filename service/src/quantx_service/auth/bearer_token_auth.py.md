# `bearer_token_auth.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Authenticates sidecar clients (not end-user subjects — that's the whole point of QuantX's challenge/response) via a static or rotating bearer token, per `09-auth-and-authorization.md`'s sidecar-client authentication model.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/auth/`
- **Depends on:** `config.py` (this package, for the configured token(s))
- **Imported by:** `main.py`/routers, as a FastAPI dependency

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `config.py`
- **Implements:** A FastAPI dependency validating the `Authorization: Bearer <token>` header.
- **Outside:** Authenticating the end-user subject — that's the challenge/response flow itself, not this file's concern (`09-auth-and-authorization.md` is explicit that QuantX authenticates the sidecar client, not the identity binding of the end subject).
- **Inside:** Token comparison against configured value(s), constant-time where applicable.
- **Security notes:** Token comparison uses a constant-time comparison to avoid a timing side-channel `(inferred: standard practice for token comparison; the docs establish bearer-token auth as the mechanism, not this specific implementation detail)`.

## Required behavior
- Validates the `Authorization: Bearer <token>` header against configured value(s).
- Rejects with `401` (mapped via `error_envelope.py`) on missing/invalid token.

## Inputs / outputs
- **In:** the `Authorization` header.
- **Out:** pass-through on valid token; `401` otherwise.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- Authenticates the sidecar *client*, not the end-user subject — identity binding of the subject is the integrating application's responsibility (`09-auth-and-authorization.md`).

## Mandatory tests this must pass
- Exercised indirectly via router tests that require authentication.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- End-subject identity binding — integrating application's job.

## Source docs
`09-auth-and-authorization.md`, `08-api-specification.md`
