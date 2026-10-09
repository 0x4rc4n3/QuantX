# `standards_catalog.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A reference catalog mapping algorithms/findings in a `CryptoBOM` to relevant compliance-standard references, so `compliance_report_generator.py` can annotate a report without embedding standards knowledge in the generator itself.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `src/quantx_compliance`
- **Depends on:** `crypto_bom_model.py` (this package)
- **Imported by:** `compliance_report_generator.py` (this package)

## Docstring contract
- **Layer:** 10
- **Depends on:** `CryptoBOM` (this package)
- **Implements:** `lookup(algorithm_id) -> list[StandardReference]` or equivalent
- **Outside:** Scanning for algorithms in the first place — `scanners/`'s job.
- **Inside:** Static reference data mapping algorithms to standards.
- **Security notes:** None — this is reference data, not a security-enforcing component.

## Required behavior
- Provides a lookup from an algorithm/finding to relevant standards references, as static reference data `(inferred exact standards covered — the docs establish that a standards catalog exists and is consulted by the report generator, not which specific standards bodies/documents it covers)`.
- Holds no scanning logic — purely a lookup table.

## Inputs / outputs
- **In:** an `AlgorithmId` or `CryptoBOM` finding.
- **Out:** a list of relevant standards references.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- `tests/test_standards_catalog.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Scanning — `scanners/`.
- Report formatting — `compliance_report_generator.py`.

## Source docs
`04-functional-requirements.md`
