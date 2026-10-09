# `main.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The FastAPI application entry point — mounts routers, installs middleware, and starts the ASGI app. Deliberately thin: composition only, no business logic (`06-system-architecture.md`'s FastAPI + Uvicorn/Gunicorn tech-stack entry).

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service`
- **Depends on:** `wiring.py` (this package, the composition root); `routers/`, `middleware/` (this package)
- **Imported by:** Uvicorn/Gunicorn, at process start (`06-system-architecture.md`)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `wiring.py`, `routers/`, `middleware/` (this package)
- **Implements:** The FastAPI `app` object, router mounting, middleware installation.
- **Outside:** Any actual request-handling logic — that's each router's job.
- **Inside:** Application assembly only.
- **Security notes:** `hybrid_tls_enforcement.py` middleware is installed here — a sidecar deployment must not silently accept non-hybrid TLS if hybrid is required (SR-1's sidecar-boundary equivalent).

## Required behavior
- Constructs the FastAPI `app`, mounts `challenge_router.py`, `verify_router.py`, `session_router.py`, and installs `hybrid_tls_enforcement.py`/`rate_limit_headers.py` middleware.
- Uses `wiring.py` as the single composition root — this file does not itself construct `AlgorithmRegistry`, `SessionOrchestrator`, or any other library object directly.

## Inputs / outputs
- **In:** none (process entry point).
- **Out:** the ASGI `app` object Uvicorn/Gunicorn serves.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- Hosts the hybrid-TLS-enforcement middleware — this is the sidecar-boundary analogue of SR-1: the sidecar must not accept a downgraded TLS posture any more than `SignatureCombiner` accepts a downgraded signature mode.

## Mandatory tests this must pass
- `tests/conftest.py` (a test client built against this app)

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Explicitly out of scope for this file
- Request-handling logic — routers.
- Composition details — `wiring.py`.

## Source docs
`06-system-architecture.md`, `08-api-specification.md`
