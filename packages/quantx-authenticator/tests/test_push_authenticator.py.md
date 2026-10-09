# `test_push_authenticator.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `PushAuthenticator.issue()`/`consume()` correctly issue and single-use-verify approvals, on the non-adversarial path.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/`
- **Depends on:** `push_authenticator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `push_authenticator.py`
- **Implements:** pytest test functions.
- **Outside:** SR-5/SR-11 adversarial scenarios — separate security tests.
- **Inside:** Genuine issue/consume round trip.
- **Security notes:** See Security notes below.

## Required behavior
- `issue()` returns a `PushApprovalRecord`.
- `consume(approval_id)` succeeds exactly once for a genuine, unexpired approval.

## Inputs / outputs
- **In:** `subject_id`, `approval_id`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `push_authenticator.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-5 (rate-limit-before-send) and SR-11 (replay) adversarial scenarios — separate files.

## Source docs
`04-functional-requirements.md`
