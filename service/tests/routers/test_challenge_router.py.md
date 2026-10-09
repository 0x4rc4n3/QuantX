# `test_challenge_router.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `POST /v1/challenges` returns a correctly-shaped response and `400`s on a malformed request.

## Part of / dependency graph
- **Package:** `service`, `tests/routers/`
- **Depends on:** `challenge_router.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** sidecar
- **Depends on:** challenge_router.py
- **Implements:** pytest test functions using the `TestClient` fixture.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below where applicable.

## Required behavior
- A valid request returns `200` with `challenge_id`, `nonce`, `required_mode`, `expires_at`.
- A malformed request body returns `400 malformed_request`.

## Inputs / outputs
- **In:** HTTP requests via the `TestClient` fixture.
- **Out:** pass/fail on response status/shape.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the test for `challenge_router.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside `challenge_router.py`.

## Source docs
`08-api-specification.md`
