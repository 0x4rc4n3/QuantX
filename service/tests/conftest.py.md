# `conftest.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Builds a FastAPI `TestClient` against the sidecar app, wired via `wiring.py` against Recipe-A-style in-memory backends, so router tests exercise real request/response handling without needing a live deployment.

## Part of / dependency graph
- **Package:** `service`, `tests/`
- **Depends on:** `main.py`, `wiring.py` (this package)
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `main.py`, `wiring.py`
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Test-client construction.
- **Security notes:** None beyond individual test files' own.

## Required behavior
- Provides a FastAPI `TestClient` wired against in-memory backends for fast, isolated router tests.

## Inputs / outputs
- **In:** nothing.
- **Out:** a `TestClient` fixture.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Assertion logic.

## Source docs
`14-directory-structure.md`
