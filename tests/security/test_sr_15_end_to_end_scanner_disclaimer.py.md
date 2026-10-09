# `test_sr_15_end_to_end_scanner_disclaimer.py`

**Package:** `root tests` · **Layer:** cross-cutting · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The full-stack, end-to-end confirmation of SR-15: the static scanner's best-effort disclaimer survives all the way through to a generated compliance report. Complements the package-internal SR-15 test with a version that spans real wiring between packages, per this file's own `tests/security/README.md` rationale.

## Part of / dependency graph
- **Package:** `root tests`, `tests/security/`
- **Depends on:** `quantx-compliance`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** cross-cutting
- **Depends on:** quantx-compliance
- **Implements:** The mandatory end-to-end confirmation of SR-15.
- **Outside:** Every other numbered SR item — one file per item.
- **Inside:** Run `StaticSourceScanner` against a sample tree, feed the result into `ComplianceReportGenerator`, and confirm the disclaimer is present in the final report output, not dropped during aggregation.
- **Security notes:** This file **is** the end-to-end enforcement check for SR-15, complementing (not replacing) the package-internal test.

## Required behavior
- Run `StaticSourceScanner` against a sample tree, feed the result into `ComplianceReportGenerator`, and confirm the disclaimer is present in the final report output, not dropped during aggregation.
- A failure here, even when the package-internal SR-15 test passes, indicates the vulnerability was reintroduced somewhere in the wiring between packages — exactly the class of bug a package-scoped test can't catch.

## Inputs / outputs
- **In:** the full wired-stack fixture from `tests/conftest.py`.
- **Out:** must hold end-to-end; a release blocker if it fails even while the package-internal test passes.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-15.** End-to-end confirmation, spanning quantx-compliance.

## Mandatory tests this must pass
- This file *is* the mandatory end-to-end SR-15 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Every other numbered SR item.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
