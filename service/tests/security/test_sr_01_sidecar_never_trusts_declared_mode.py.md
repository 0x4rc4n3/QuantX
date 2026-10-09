# `test_sr_01_sidecar_never_trusts_declared_mode.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `POST /v1/verify` never accepts a client-supplied mode override — the sidecar boundary's own instance of SR-1, on top of `quantx-combiners`'s own SR-1 test at the library level.

## Part of / dependency graph
- **Package:** `service`, `tests/security/`
- **Depends on:** `verify_router.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `verify_router.py`
- **Implements:** The mandatory automated security test for SR-1 at the sidecar boundary.
- **Outside:** The library-level SR-1 test — `quantx-combiners`'s own `test_sr_01_hybrid_downgrade_rejected.py`.
- **Inside:** HTTP-level mode-override attempts against `POST /v1/verify`.
- **Security notes:** This file **is** the sidecar-boundary SR-1 enforcement check.

## Required behavior
- Send a `POST /v1/verify` request with an injected/overridden mode field in the request body that doesn't match the server's configured `required_mode` for that role.
- Confirm the sidecar's response is a rejection (`401 verification_failed` or equivalent) regardless of what the request body claims — `required_mode` is sourced from the wired registry role via `wiring.py`, never from request content.

## Inputs / outputs
- **In:** an HTTP request with a mode-override attempt.
- **Out:** must reject; a release blocker if this ever succeeds.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A client attempts to smuggle a mode override in the request body → has no effect (SR-1, mirrored at the sidecar boundary, `13-error-and-edge-cases.md`).

## Security notes
- **SR-1 (sidecar boundary).**

## Mandatory tests this must pass
- This file *is* the mandatory sidecar-boundary SR-1 test.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- The library-level SR-1 test — separate package.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`, `08-api-specification.md`
