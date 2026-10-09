# `quantx_compliance` — package source root

## What this is
Layer 10: the crypto bill-of-materials model, standards catalog, report generator, and the two scanners that populate the model.

## Part of
`quantx-compliance`, Layer 10.

## Contains
- `crypto_bom_model.py` — the data model, no scanning logic of its own
- `standards_catalog.py` — reference data
- `compliance_report_generator.py` — formatting/aggregation only (FR-10.4)
- `scanners/` — the two scanners

## Why divided this way
Scanning, standards reference data, and report formatting are three independently-testable concerns per `14-directory-structure.md`'s atomicity rule; `compliance_report_generator.py`'s FR-10.4 constraint ("no scanning logic or standards data of its own") is easiest to verify precisely because those two concerns live in separate files it merely reads from.

## Dependency rules
- `compliance_report_generator.py` depends on `crypto_bom_model.py` and `standards_catalog.py`, never on `scanners/` directly — it reads whatever `CryptoBOM` it's given, regardless of which scanner populated it.

## Source docs
`04-functional-requirements.md`, `14-directory-structure.md`
