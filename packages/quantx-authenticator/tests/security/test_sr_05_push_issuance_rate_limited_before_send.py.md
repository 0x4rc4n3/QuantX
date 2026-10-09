# `test_sr_05_push_issuance_rate_limited_before_send.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `PushAuthenticator` checks its rate limiter before attempting to send a push notification, not merely at verification time.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/security/`
- **Depends on:** `push_authenticator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `push_authenticator.py`
- **Implements:** The mandatory automated security test for SR-5.
- **Outside:** SR-11 replay rejection — separate file.
- **Inside:** Rate-limit-before-send ordering.
- **Security notes:** This file **is** the SR-5 enforcement check.

## Required behavior
- Exceed the push-issuance rate limit for a subject, then attempt `issue()` again.
- Confirm no send attempt is made (via a spy/mock on the send path) once the limiter has tripped — the check happens before send, not merely recorded after.

## Inputs / outputs
- **In:** repeated `issue()` calls past the limit.
- **Out:** must reject before any send attempt.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-5.** Push-notification issuance is rate-limited before sending, not just verification.

## Mandatory tests this must pass
- This file *is* the mandatory SR-5 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- SR-11 — separate file.

## Source docs
`10-security-requirements.md`, `04-functional-requirements.md`
