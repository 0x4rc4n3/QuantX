# `test_totp_rate_limiter_independent_of_session_limiter.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms TOTP verification's rate limiter is a genuinely separate instance from Layer 4's session limiter — hammering one does not affect the other (FR-5.2).

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/security/`
- **Depends on:** `totp_provider.py`; `session_orchestrator.py` (Layer 4, for cross-limiter comparison)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `totp_provider.py`, Layer 4's `session_orchestrator.py`
- **Implements:** The mandatory foundational test for FR-5.2.
- **Outside:** Push-issuance rate limiting — separate SR-5 test.
- **Inside:** Cross-limiter independence.
- **Security notes:** This file **is** the FR-5.2 enforcement check.

## Required behavior
- Trip the TOTP rate limiter (repeated bad codes for one subject) and confirm the Layer-4 session limiter's state for that same subject is unaffected — a legitimate primary-factor attempt still succeeds.
- Trip the Layer-4 session limiter and confirm TOTP verification for that subject is still independently rate-gated on its own terms, not blocked or unblocked by the session limiter's state.

## Inputs / outputs
- **In:** repeated attempts against each limiter independently.
- **Out:** confirms no cross-limiter interference.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-5.2.** TOTP verification has its own rate limiter, independent of the Layer 4 session limiter.

## Mandatory tests this must pass
- This file *is* the mandatory FR-5.2 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- SR-5 push-issuance rate limiting — separate file.

## Source docs
`04-functional-requirements.md`, `03-user-stories-and-flows.md`
