# `test_tls_inspector.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `TlsInspector.inspect()` correctly parses a test TLS endpoint's leaf certificate via `cryptography.x509`, on the non-adversarial/authenticated path (SR-13's tagging behavior is the dedicated security test).

## Part of / dependency graph
- **Package:** `quantx-compliance`, `tests/scanners/`
- **Depends on:** `tls_inspector.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 10
- **Depends on:** `tls_inspector.py`
- **Implements:** pytest test functions.
- **Outside:** SR-13 trust-level tagging — separate file.
- **Inside:** Authenticated-probe certificate parsing.
- **Security notes:** Confirms FR-10.3's `cryptography.x509`-only parsing (no `openssl` shell-out).

## Required behavior
- Against a known-good test TLS endpoint/certificate, the authenticated probe correctly reports signature algorithm and key size.
- Confirms parsing goes through `cryptography.x509.load_der_x509_certificate`, never a subprocess call to `openssl`.

## Inputs / outputs
- **In:** a test TLS endpoint.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-10.3.** No `openssl` shell-out — verified here directly, not just asserted.

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `tls_inspector.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-13 — separate file.

## Source docs
`04-functional-requirements.md`
