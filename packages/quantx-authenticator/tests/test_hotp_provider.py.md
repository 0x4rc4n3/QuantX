# `test_hotp_provider.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `HotpProvider.verify()` accepts a correct code for the current counter value and increments the counter on success.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/`
- **Depends on:** `hotp_provider.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `hotp_provider.py`
- **Implements:** pytest test functions.
- **Outside:** TOTP's time-based logic.
- **Inside:** Counter-based code verification and increment.
- **Security notes:** None beyond confirming counter-increment discipline.

## Required behavior
- A correct code for the current counter value verifies successfully and increments the counter.
- An incorrect code fails verification and does not advance the counter.

## Inputs / outputs
- **In:** HOTP codes.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `hotp_provider.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- TOTP's time-based logic.

## Source docs
`07-database-design.md`
