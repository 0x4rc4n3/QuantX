# `crypto_bom_model.py`

**Package:** `quantx-compliance` · **Layer:** 10 — Observability & compliance · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The crypto bill-of-materials value model — the structured record of which algorithms are in use where, that scanners populate and `compliance_report_generator.py` reads to produce human-facing reports. Holds no scanning logic itself (FR-10.4).

## Part of
- **Depends on:** `quantx_core.types.algorithm_id.AlgorithmId` (Layer 0)
- **Imported by:** `static_source_scanner.py`, `tls_inspector.py` (populate it); `compliance_report_generator.py`, `standards_catalog.py` (read it)

## Shape
- `CryptoBOM` — a collection of findings, each identifying an algorithm, where it was found (source file, or TLS endpoint), and the finding's trust level (for TLS findings, SR-13).
- Holds no scanning logic of its own — purely a data model that scanners populate and the report generator reads (FR-10.4).
- Every entry produced by `static_source_scanner.py` carries that scanner's best-effort disclaimer, attached at the point of output (SR-15) — this model's shape is what makes that attachment possible per-finding, not just once at the top of a report `(inferred: the docs require the disclaimer to be attached to output; whether that's a per-finding field or a report-level banner is left to implementation, but a per-finding field is the reading most consistent with SR-15's own wording, "attached to any output it produces")`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`
