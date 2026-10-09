# `session_router.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Implements the session-token validation endpoint(s) — `validate(token)` exposed over HTTP, per `08-api-specification.md`.

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
- **Security notes:** No `SR-x` item specific to this router — token validity is entirely `SessionOrchestrator`'s concern.

## Required behavior
- Parses the incoming request per `08-api-specification.md`'s schema.
- Calls `SessionOrchestrator.validate()` via the wired dependency.
- Shapes the response per the documented schema.

## Inputs / outputs
- **In:** an HTTP request carrying a session token.
- **Out:** a JSON validity response per `08-api-specification.md`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- An unknown or expired token → the documented not-found/invalid response, via `error_envelope.py`, never a raw exception surfaced to the client.

## Security notes
- No `SR-x` item specific to this router — token validity is entirely `SessionOrchestrator`'s concern.

## Mandatory tests this must pass
- `tests/routers/test_session_router.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.

## Explicitly out of scope for this file
- Business logic — delegates entirely to the library objects wired in `wiring.py`.

## Source docs
`08-api-specification.md`
