# `verify_router.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Implements `POST /v1/verify` — the sidecar's highest-stakes endpoint: verifies a signed response against a previously-issued challenge, **never trusting a client-declared mode** (SR-1's sidecar-boundary enforcement).

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/routers/`
- **Depends on:** `wiring.py` (this package, via FastAPI dependency injection)
- **Imported by:** `main.py` (mounted onto the FastAPI app)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `wiring.py`'s constructed dependencies
- **Implements:** The HTTP endpoint(s) this router owns, per `08-api-specification.md`.
- **Outside:** Any business logic beyond translating HTTP <-> library calls — the library does the actual work.
- **Inside:** Request parsing/validation, calling into the wired library objects, response shaping per `08-api-specification.md`'s response schemas.
- **Security notes:** **SR-1 (sidecar boundary).** This router must never trust a declared mode from the wire — the dedicated test for this router is `test_sr_01_sidecar_never_trusts_declared_mode.py`, at the repo root of `service/tests/security/`.

## Required behavior
- Parses the incoming request per `08-api-specification.md`'s schema.
- Calls into `SessionOrchestrator`/`SignatureCombiner` via wired dependencies — the actual mode enforcement (SR-1) happens inside the library, not in this router's own code.
- Never reads a `declared_mode`-style field from the request body and uses it to decide acceptance — the sidecar's `required_mode` comes from the wired `AlgorithmRegistry` role, identically to how the library itself never trusts wire-declared mode.

## Inputs / outputs
- **In:** an HTTP `POST /v1/verify` request with the signed response.
- **Out:** a JSON success/failure response per `08-api-specification.md`, or a mapped error envelope.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A client attempts to smuggle a mode override in the request body → has no effect — `required_mode` is sourced from the wired registry role, never from request content (SR-1, mirrored at the sidecar boundary).

## Security notes
- **SR-1 (sidecar boundary).** This router must never trust a declared mode from the wire — the dedicated test for this router is `test_sr_01_sidecar_never_trusts_declared_mode.py`, at the repo root of `service/tests/security/`.

## Mandatory tests this must pass
- `tests/routers/test_verify_router.py`
- `tests/security/test_sr_01_sidecar_never_trusts_declared_mode.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.

## Explicitly out of scope for this file
- Business logic — delegates entirely to the library objects wired in `wiring.py`.

## Source docs
`10-security-requirements.md`, `08-api-specification.md`
