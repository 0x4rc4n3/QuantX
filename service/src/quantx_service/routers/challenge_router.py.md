# `challenge_router.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Implements `POST /v1/challenges` — issues a challenge via `ChallengeIssuer`, per `08-api-specification.md`'s request/response schema.

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
- **Security notes:** No `SR-x` item is specific to this router beyond standard input validation — the security-critical decisions (mode enforcement, replay, rate limiting) all happen inside the library objects this router calls.

## Required behavior
- Parses the incoming request per `08-api-specification.md`'s schema for this endpoint.
- Calls `ChallengeIssuer.issue()` via the wired dependency — never constructs its own.
- Shapes the response per the documented schema, including `required_mode` and `expires_at`.

## Inputs / outputs
- **In:** an HTTP `POST /v1/challenges` request.
- **Out:** a JSON response containing `challenge_id`, `nonce`, `required_mode`, `expires_at`, per `08-api-specification.md`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A malformed request body → `400 malformed_request`, via `error_envelope.py`'s standard shape.

## Security notes
- No `SR-x` item is specific to this router beyond standard input validation — the security-critical decisions (mode enforcement, replay, rate limiting) all happen inside the library objects this router calls.

## Mandatory tests this must pass
- `tests/routers/test_challenge_router.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.

## Explicitly out of scope for this file
- Business logic — delegates entirely to the library objects wired in `wiring.py`.

## Source docs
`08-api-specification.md`
