# `static_source_scanner.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Scans source code for cryptographic algorithm usage and populates a `CryptoBOM` — always with a stated best-effort disclaimer attached to its output, never presented as an exhaustive/authoritative audit (FR-10.1, SR-15).

## Part of / dependency graph
- **Package:** `quantx-compliance`, `src/quantx_compliance/scanners/`
- **Depends on:** `crypto_bom_model.py` (this package)
- **Imported by:** `compliance_report_generator.py` (indirectly, via the `CryptoBOM` it populates)

## Docstring contract
- **Layer:** 10
- **Depends on:** `CryptoBOM` (this package)
- **Implements:** `scan(source_paths) -> CryptoBOM`
- **Outside:** TLS/network-based inspection — `tls_inspector.py`'s job.
- **Inside:** Static pattern-matching over source code for algorithm usage.
- **Security notes:** SR-15 in full: every output states plainly this is a best-effort scan, not an exhaustive audit.

## Required behavior
- States plainly, every time, that this is a best-effort scan, not an exhaustive audit (FR-10.1, SR-15) — the disclaimer is attached to the output itself, not just documented once somewhere separate from what gets produced.
- Populates a `CryptoBOM` with findings tagged by source location.

## Inputs / outputs
- **In:** a set of source paths.
- **Out:** a `CryptoBOM`, every finding/output carrying the best-effort disclaimer.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-15.** Best-effort disclaimer attached to every output, always — this is a release-blocking property if ever dropped.

## Mandatory tests this must pass
- `tests/scanners/test_static_source_scanner.py`
- `tests/security/test_sr_15_scanner_disclaimer_attached_to_output.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- TLS/network inspection — `tls_inspector.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`
