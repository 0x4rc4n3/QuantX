# `test_sr_01_end_to_end_hybrid_downgrade.py`

**Package:** `root tests` · **Layer:** cross-cutting · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The full-stack, end-to-end confirmation of SR-1: SignatureCombiner never accepts a mode not matching required_mode. Complements the package-internal SR-1 test with a version that spans real wiring between packages, per this file's own `tests/security/README.md` rationale.

## Part of / dependency graph
- **Package:** `root tests`, `tests/security/`
- **Depends on:** `quantx-combiners`; `quantx-session`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** cross-cutting
- **Depends on:** quantx-combiners, quantx-session
- **Implements:** The mandatory end-to-end confirmation of SR-1.
- **Outside:** Every other numbered SR item — one file per item.
- **Inside:** Strip the PQC component from a genuine hybrid signature and rewrite the mode byte, at the full `default_setup() → start() → finish()` flow level (not just unit-testing `SignatureCombiner` directly) — confirm `finish()` rejects, end-to-end.
- **Security notes:** This file **is** the end-to-end enforcement check for SR-1, complementing (not replacing) the package-internal test.

## Required behavior
- Strip the PQC component from a genuine hybrid signature and rewrite the mode byte, at the full `default_setup() → start() → finish()` flow level (not just unit-testing `SignatureCombiner` directly) — confirm `finish()` rejects, end-to-end.
- A failure here, even when the package-internal SR-1 test passes, indicates the vulnerability was reintroduced somewhere in the wiring between packages — exactly the class of bug a package-scoped test can't catch.

## Inputs / outputs
- **In:** the full wired-stack fixture from `tests/conftest.py`.
- **Out:** must hold end-to-end; a release blocker if it fails even while the package-internal test passes.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-1.** End-to-end confirmation, spanning quantx-combiners, quantx-session.

## Mandatory tests this must pass
- This file *is* the mandatory end-to-end SR-1 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Every other numbered SR item.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
