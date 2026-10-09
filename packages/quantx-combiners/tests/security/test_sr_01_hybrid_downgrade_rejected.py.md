# `test_sr_01_hybrid_downgrade_rejected.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The mandatory hybrid-downgrade test (mandatory test 1, `10-security-requirements.md`): strip the PQC component from a real hybrid signature, alter the declared-mode byte, call `verify()` — must return `False` before any further crypto executes.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/security/`
- **Depends on:** `signature_combiner.py`; `signature_mode_enforcement.py`; `signature_wire_format.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 2
- **Depends on:** The full signature-combining path.
- **Implements:** The mandatory automated security test for SR-1.
- **Outside:** SR-7 (that's the KEM-side test).
- **Inside:** Constructing a genuine HYBRID signature via `conftest.py`'s fixture, stripping the PQC component, rewriting the declared-mode byte, and confirming rejection.
- **Security notes:** This file **is** the SR-1 enforcement check.

## Required behavior
- Construct a genuine `HYBRID` signature using real classical + PQC adapters.
- Strip the PQC component from the wire bytes and rewrite the declared-mode byte to make the truncated signature look self-consistent (e.g. as `CLASSICAL_ONLY`).
- Call `SignatureCombiner.verify()` with `required_mode=HYBRID` still set at the combiner level — confirm the result is `False`, and confirm (via a spy/mock or explicit ordering check) that this rejection happens in `signature_mode_enforcement.py`, before any `Verifier.verify()` call executes.

## Inputs / outputs
- **In:** a tampered wire-format signature.
- **Out:** must be `False`; a release blocker if this ever returns `True` or raises.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- This *is* the edge case named in `13-error-and-edge-cases.md`'s wire/input-handling table.

## Security notes
- **SR-1.** The single highest-priority test in the entire suite — this is the literal scenario SR-1 exists to prevent.

## Mandatory tests this must pass
- This file *is* the mandatory SR-1 test.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- SR-7 (KEM substitution) — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`, `03-user-stories-and-flows.md`
