# `test_sr_15_scanner_disclaimer_attached_to_output.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `StaticSourceScanner`'s every output carries the best-effort disclaimer — never presented as an exhaustive/authoritative audit.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/security/`
- **Depends on:** `static_source_scanner.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `static_source_scanner.py`
- **Implements:** The mandatory automated security test for SR-15.
- **Outside:** Scan-accuracy itself — separate file.
- **Inside:** Disclaimer presence on every output.
- **Security notes:** This file **is** the SR-15 enforcement check.

## Required behavior
- Run `scan()` against any source tree, including an empty one.
- Confirm the resulting output (`CryptoBOM` and/or its findings) carries the best-effort disclaimer, every time, including when zero findings are produced.

## Inputs / outputs
- **In:** any source tree, including empty.
- **Out:** disclaimer must always be present.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-15.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-15 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Scan-accuracy itself — separate file.

## Source docs
`10-security-requirements.md`, `04-functional-requirements.md`
