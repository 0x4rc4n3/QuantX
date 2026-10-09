# `test_compliance_report_generator.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ComplianceReportGenerator.generate()` correctly assembles a report from a `CryptoBOM` and `standards_catalog.py` lookups without inventing any fact of its own.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/`
- **Depends on:** `compliance_report_generator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `compliance_report_generator.py`
- **Implements:** pytest test functions.
- **Outside:** Scanning and standards-data content.
- **Inside:** Aggregation/formatting correctness.
- **Security notes:** Confirms FR-10.4 at the unit level — no invented facts.

## Required behavior
- Every fact in the generated report traces to a `CryptoBOM` finding or `standards_catalog.py` lookup — the test asserts no report content exists that isn't attributable to one of those two sources.
- Trust-level tags and disclaimers from the input `CryptoBOM` survive into the output unchanged.

## Inputs / outputs
- **In:** a sample `CryptoBOM`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `compliance_report_generator.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Scanning and standards-data content.

## Source docs
`04-functional-requirements.md`
