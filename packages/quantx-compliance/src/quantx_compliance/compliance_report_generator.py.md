# `compliance_report_generator.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Formats a `CryptoBOM` plus `standards_catalog.py` lookups into a human-facing report. Holds no scanning logic and no standards data of its own — purely a formatting/aggregation layer (FR-10.4).

## Part of / dependency graph
- **Package:** `quantx-compliance`, `src/quantx_compliance`
- **Depends on:** `crypto_bom_model.py`, `standards_catalog.py` (this package)
- **Imported by:** Integrating-application/CLI reporting entry points `(inferred consumer)`

## Docstring contract
- **Layer:** 10
- **Depends on:** `CryptoBOM`, `standards_catalog.py` (this package)
- **Implements:** `generate(bom) -> Report` (or a rendered string/document)
- **Outside:** Scanning (`scanners/`) and standards reference data (`standards_catalog.py`'s own content) — this file only formats/aggregates.
- **Inside:** Report assembly and formatting.
- **Security notes:** FR-10.4: no scanning logic or standards data of its own — every fact in the output traces back to a scanner finding or a catalog lookup, never invented here.

## Required behavior
- Has no scanning logic or standards data of its own (FR-10.4) — every fact in the generated report traces to a `CryptoBOM` finding or a `standards_catalog.py` lookup.
- Preserves each finding's trust-level tagging (SR-13) and best-effort disclaimer (SR-15) through to the final report — never drops or waters down either while formatting.

## Inputs / outputs
- **In:** a `CryptoBOM`.
- **Out:** a formatted report (structure/format not specified further in the available docs).

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-13 / SR-15 (pass-through).** This file must not lose either tag while formatting — it's a pure aggregation layer, not a place either disclosure gets re-derived or summarized away.

## Mandatory tests this must pass
- `tests/test_compliance_report_generator.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Scanning.
- Standards reference data itself.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`
