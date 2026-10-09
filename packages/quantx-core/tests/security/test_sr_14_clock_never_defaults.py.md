# `test_sr_14_clock_never_defaults.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms no component in this package uses an `x or default` pattern against a wall-clock read instead of its injected `Clock`.

## Part of / dependency graph
- **Package:** `quantx-core`, `packages/quantx-core/tests/security`
- **Depends on:** `system_clock.py`; `in_memory_replay_store.py`; `in_memory_rate_limiter.py`; `in_memory_kv_store.py`
- **Imported by:** Nothing — test files are leaves in the dependency graph.

## Docstring contract
- **Layer:** 0
- **Depends on:** `system_clock.py`, `in_memory_replay_store.py`, `in_memory_rate_limiter.py`, `in_memory_kv_store.py`
- **Implements:** The mandatory automated security test for SR-14 (`10-security-requirements.md`).
- **Outside:** Anything not directly required to prove or disprove this one SR item.
- **Inside:** The specific attack/failure scenario named in Required behavior below.
- **Security notes:** This file **is** the enforcement check for SR-14.

## Required behavior
- Inject a fake `Clock` returning a known, controlled timestamp.
- Confirm every timestamp-consuming impl in this package (`in_memory_replay_store.py`, `in_memory_rate_limiter.py`, `in_memory_kv_store.py`'s TTL logic) uses that injected value, not a real wall-clock read, for any expiry/window computation.

## Inputs / outputs
- **In:** fixtures from `conftest.py`, crafted adversarial input specific to this SR item.
- **Out:** pass/fail; a failing run here is a release blocker per `10-security-requirements.md`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-14.** This file is the named, dedicated enforcement test for SR-14 — per `14-directory-structure.md`'s naming convention, its filename alone answers "where's the test for SR-14".

## Mandatory tests this must pass
- This file *is* the mandatory test for SR-14 — nothing else satisfies it.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Testing any SR item other than the one named in this file's title.

## Source docs
`10-security-requirements.md`
