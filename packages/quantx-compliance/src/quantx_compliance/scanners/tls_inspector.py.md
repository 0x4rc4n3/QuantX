# `tls_inspector.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Probes a TLS endpoint and reports its leaf certificate's signature algorithm and key size, parsed via `cryptography.x509.load_der_x509_certificate` directly — never shelling out to `openssl` (FR-10.3). Runs an authenticated probe by default; a separate, explicitly opt-in permissive probe exists for cases where authentication itself is impossible, and its findings are tagged as unverified (FR-10.2, SR-13).

## Part of / dependency graph
- **Package:** `quantx-compliance`, `src/quantx_compliance/scanners/`
- **Depends on:** `crypto_bom_model.py` (this package); `cryptography`'s `x509.load_der_x509_certificate` (D1/FR-10.3 — no shelling out to `openssl`)
- **Imported by:** `compliance_report_generator.py` (indirectly, via the `CryptoBOM` it populates)

## Docstring contract
- **Layer:** 10
- **Depends on:** `CryptoBOM` (this package); `cryptography`'s `x509` module
- **Implements:** `inspect(endpoint, mode='authenticated') -> CryptoBOM` (or equivalent, with `mode='permissive'` as an explicit opt-in)
- **Outside:** Static source scanning — `static_source_scanner.py`'s job.
- **Inside:** TLS handshake/probe and certificate parsing.
- **Security notes:** FR-10.2/SR-13 in full: authenticated by default, permissive findings tagged unverified.

## Required behavior
- Runs an authenticated probe by default (FR-10.2).
- A separate, explicitly opt-in permissive probe exists for cases where authentication itself is impossible — its findings are tagged `unverified` at the finding level, never silently merged with authenticated findings (SR-13).
- Parses the leaf certificate itself via `cryptography.x509.load_der_x509_certificate` and reports its signature algorithm and key size — never by shelling out to `openssl` (FR-10.3).

## Inputs / outputs
- **In:** a TLS endpoint, `mode` (`authenticated`/`permissive`).
- **Out:** a `CryptoBOM` populated with the leaf certificate's signature algorithm and key size, tagged by trust level.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- TLS inspection of an endpoint that can't be authenticated (e.g. self-signed, expired) is attempted via the explicitly opt-in permissive probe, and any resulting finding is tagged unverified — never silently merged with authenticated findings (SR-13, `13-error-and-edge-cases.md`).

## Security notes
- **SR-13.** Permissive-probe findings tagged `unverified`, always, never merged silently with authenticated findings.
- **FR-10.3.** Certificate parsing via `cryptography.x509`, never `openssl` shell-out — a shell-out introduces a command-injection-class surface this in-process parse avoids entirely.

## Mandatory tests this must pass
- `tests/scanners/test_tls_inspector.py`
- `tests/security/test_sr_13_tls_findings_tagged_by_trust_level.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Static source scanning — `static_source_scanner.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
