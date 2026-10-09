# `test_sr_12_end_to_end_threshold_duplicate_key.py`

**Package:** `root tests` · **Layer:** cross-cutting · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The full-stack, end-to-end confirmation of SR-12: a threshold policy with a duplicate key is rejected end-to-end, before it could ever be used in a real approval flow. Complements the package-internal SR-12 test with a version that spans real wiring between packages, per this file's own `tests/security/README.md` rationale.

## Part of / dependency graph
- **Package:** `root tests`, `tests/security/`
- **Depends on:** `quantx-threshold`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** cross-cutting
- **Depends on:** quantx-threshold
- **Implements:** The mandatory end-to-end confirmation of SR-12.
- **Outside:** Every other numbered SR item — one file per item.
- **Inside:** Attempt to construct and then use a duplicate-key policy through the full `ThresholdManager` flow, confirming rejection happens at construction, before any approval is ever processed.
- **Security notes:** This file **is** the end-to-end enforcement check for SR-12, complementing (not replacing) the package-internal test.

## Required behavior
- Attempt to construct and then use a duplicate-key policy through the full `ThresholdManager` flow, confirming rejection happens at construction, before any approval is ever processed.
- A failure here, even when the package-internal SR-12 test passes, indicates the vulnerability was reintroduced somewhere in the wiring between packages — exactly the class of bug a package-scoped test can't catch.

## Inputs / outputs
- **In:** the full wired-stack fixture from `tests/conftest.py`.
- **Out:** must hold end-to-end; a release blocker if it fails even while the package-internal test passes.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-12.** End-to-end confirmation, spanning quantx-threshold.

## Mandatory tests this must pass
- This file *is* the mandatory end-to-end SR-12 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Every other numbered SR item.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
