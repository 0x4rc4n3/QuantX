# `test_session_orchestrator.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `SessionOrchestrator.finish()`/`validate()` correctly gate on primary-factor verification and mint a well-formed `SessionToken` on success, using genuine (non-adversarial) inputs.

## Part of / dependency graph
- **Package:** `quantx-session`, `tests/`
- **Depends on:** `session_orchestrator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 4
- **Depends on:** `session_orchestrator.py`
- **Implements:** pytest test functions.
- **Outside:** The SR-10 mint-ordering adversarial test and the replay/rate-limit test — separate files in `security/`.
- **Inside:** Genuine-path `finish()`/`validate()` behavior.
- **Security notes:** See Security notes below.

## Required behavior
- A genuine signed response against a real challenge mints a `SessionToken` with `factors_completed` populated.
- `validate(token)` returns `True` for a live, unexpired token and `False` for an unknown/expired one.
- A tampered (invalid) signed response is rejected, no token minted.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the integration test for `session_orchestrator.py`'s non-adversarial behavior.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-10 adversarial mint-ordering, replay, and rate-limit tests — `security/`.

## Source docs
`04-functional-requirements.md`, `03-user-stories-and-flows.md`
