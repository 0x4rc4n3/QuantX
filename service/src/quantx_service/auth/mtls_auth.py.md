# `mtls_auth.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Authenticates sidecar clients via mutual TLS, as an alternative to bearer-token auth, per `09-auth-and-authorization.md`.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/auth/`
- **Depends on:** `config.py` (this package, for trusted CA configuration)
- **Imported by:** `main.py`/routers, as a FastAPI dependency, where mTLS is the configured mode

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `config.py`
- **Implements:** A FastAPI dependency validating the client certificate presented at the TLS layer.
- **Outside:** Bearer-token auth — the alternative mechanism, `bearer_token_auth.py`.
- **Inside:** Client-certificate validation against configured trusted CAs.
- **Security notes:** A separate, alternative client-authentication mechanism from `bearer_token_auth.py`. A deployment enables exactly one; configuring both makes startup fail (E6, D-016).

## Required behavior
- Validates the client certificate presented at the TLS layer against configured trusted CAs.
- Rejects with `401` (mapped via `error_envelope.py`) on missing/untrusted certificate.

## Inputs / outputs
- **In:** the TLS client certificate.
- **Out:** pass-through on valid cert; `401` otherwise.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client certificate missing or not verifiable: reject with the standard auth error and never fall through to another method.

## Security notes
- Works alongside `hybrid_tls_enforcement.py` middleware, which separately enforces the hybrid TLS group requirement — this file authenticates the client identity, that middleware enforces the negotiated group.

## Mandatory tests this must pass
- Exercised indirectly via router tests that require authentication.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Bearer-token auth — the alternative mechanism.

## Source docs
`09-auth-and-authorization.md`, `08-api-specification.md`
