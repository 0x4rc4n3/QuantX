# `test_totp_provider.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `TotpProvider.verify()` accepts a correct, time-window-valid code and rejects an incorrect one, using test-fixture secrets.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/`
- **Depends on:** `totp_provider.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `totp_provider.py`
- **Implements:** pytest test functions.
- **Outside:** The independent-rate-limiter check — separate security test.
- **Inside:** Correct/incorrect code verification.
- **Security notes:** None beyond FR-5.1's gating behavior, confirmed here at the unit level.

## Required behavior
- A correct code for the current time window verifies successfully.
- An incorrect or expired-window code fails verification.

## Inputs / outputs
- **In:** TOTP codes.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `totp_provider.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Rate-limiter independence — separate security test.

## Source docs
`04-functional-requirements.md`
