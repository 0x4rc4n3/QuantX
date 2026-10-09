# `test_sr_13_tls_findings_tagged_by_trust_level.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `TlsInspector`'s permissive-probe findings are tagged `unverified` and are never silently merged with authenticated findings.

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/security/`
- **Depends on:** `tls_inspector.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `tls_inspector.py`
- **Implements:** The mandatory automated security test for SR-13.
- **Outside:** Certificate-parsing correctness — separate file.
- **Inside:** Trust-level tagging across both probe modes.
- **Security notes:** This file **is** the SR-13 enforcement check.

## Required behavior
- Run the permissive probe against an endpoint that can't be authenticated (e.g. self-signed) → confirm the resulting finding is tagged `unverified`.
- Run the authenticated probe against a properly-signed endpoint → confirm that finding is not tagged `unverified`.
- Confirm the two are never merged into a single untagged finding set.

## Inputs / outputs
- **In:** authenticated and unauthenticatable test endpoints.
- **Out:** must tag correctly, never merge untagged.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- TLS inspection of an endpoint that can't be authenticated is attempted via the explicitly opt-in permissive probe, and any resulting finding is tagged unverified — never silently merged with authenticated findings (SR-13, `13-error-and-edge-cases.md`).

## Security notes
- **SR-13.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-13 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Certificate-parsing correctness — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
