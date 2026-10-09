# `quantx-compliance/tests/security/`

## What this is
Layer 10's two security tests: SR-13 (TLS trust-level tagging) and SR-15 (scanner disclaimer attachment).

## Part of
`quantx-compliance`, Layer 10.

## Contains
- `test_sr_13_tls_findings_tagged_by_trust_level.py` — SR-13
- `test_sr_15_scanner_disclaimer_attached_to_output.py` — SR-15

## Why divided this way
Named `test_sr_<NN>_*` per `14-directory-structure.md`'s convention.

## Dependency rules
- SR-13 test depends on `tls_inspector.py`; SR-15 test depends on `static_source_scanner.py`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
