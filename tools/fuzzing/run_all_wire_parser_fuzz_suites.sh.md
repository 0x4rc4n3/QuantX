# `run_all_wire_parser_fuzz_suites.sh`

**Location:** `tools/fuzzing/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Runs both mandatory wire-parser fuzz suites (`test_signature_wire_format_fuzz.py`, `test_kem_wire_format_fuzz.py`) as one command — the operational form of `10-security-requirements.md`'s mandatory test 5 and its stated rule that "any new Layer 2+ component introducing a new attack surface gets its own test in this category before merge, not after."

## Required contents / behavior
- Invokes `pytest` against `packages/quantx-combiners/tests/security/test_signature_wire_format_fuzz.py` and `test_kem_wire_format_fuzz.py`.
- Exits non-zero on any failure, suitable for a CI gate.
- As new Layer 2+ wire-parsers are added, this script's job is to be the one place that grows to include them — new fuzz suites are added here, not left to be discovered ad hoc.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`10-security-requirements.md`
