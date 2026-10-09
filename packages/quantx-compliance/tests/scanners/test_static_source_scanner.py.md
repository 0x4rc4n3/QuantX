# `test_static_source_scanner.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `StaticSourceScanner.scan()` finds known crypto-usage patterns in a sample source tree, on the non-adversarial path (SR-15's disclaimer-attachment is the dedicated security test).

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/scanners/`
- **Depends on:** `static_source_scanner.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `static_source_scanner.py`
- **Implements:** pytest test functions.
- **Outside:** SR-15 disclaimer-attachment — separate file.
- **Inside:** Scan-accuracy on a known sample tree.
- **Security notes:** None beyond structural scan accuracy.

## Required behavior
- Scanning a temp source tree with known crypto-usage patterns produces a `CryptoBOM` with matching findings.

## Inputs / outputs
- **In:** a temp source tree.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `static_source_scanner.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-15 — separate file.

## Source docs
`04-functional-requirements.md`
