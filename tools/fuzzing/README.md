# `fuzzing/` — wire-parser fuzz suite runner

## What this is
A convenience script running both mandatory wire-parser fuzz suites (`test_signature_wire_format_fuzz.py`, `test_kem_wire_format_fuzz.py`) together, so CI (or a developer) can run mandatory test 5 as one command.

## Part of
`tools/`.

## Contains
- `run_all_wire_parser_fuzz_suites.sh`

## Why divided this way
A thin convenience wrapper, kept out of `packages/quantx-combiners/tests/` itself since it's a CI/dev runner, not a test.

## Dependency rules
- Invokes `packages/quantx-combiners/tests/security/test_signature_wire_format_fuzz.py` and `test_kem_wire_format_fuzz.py` — never duplicates their logic.

## Source docs
`10-security-requirements.md`
