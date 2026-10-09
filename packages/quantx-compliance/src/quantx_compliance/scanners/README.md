# `scanners/` — crypto-usage scanners

## What this is
The two scanners that populate a `CryptoBOM`: static source-code scanning and TLS endpoint inspection.

## Part of
`quantx-compliance`, Layer 10.

## Contains
- `static_source_scanner.py` — best-effort static scan, disclaimer attached to output (SR-15)
- `tls_inspector.py` — authenticated-by-default TLS probe, permissive findings tagged unverified (SR-13)

## Why divided this way
Two structurally unrelated scanning mechanisms (static analysis vs. live network probing), each with its own disclosure obligation, kept in separate files per `14-directory-structure.md`.

## Dependency rules
- Neither scanner imports the other.
- Both populate `crypto_bom_model.py`'s `CryptoBOM` — neither holds report-formatting logic (that's `compliance_report_generator.py`, one level up).

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `14-directory-structure.md`
