# `signature_mode_enforcement.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (Signature) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-1).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/signature_combiner.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Isolates the one decision in the whole signature path that must never be influenced by wire data: whether a signature's declared mode matches the server's `required_mode`. Split out of `signature_combiner.py` specifically so this check can be reviewed, tested, and reasoned about without also holding wire-parsing or verification-orchestration logic in view at the same time (`14-directory-structure.md`'s stated reason for this split).

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/signature/`
- **Depends on:** `quantx_core.types.mode.Mode` (Layer 0 type)
- **Imported by:** `signature_combiner.py` only.
- **Sideways-import note:** Nothing from `signature_wire_format.py` — this file receives already-parsed mode + component data, it doesn't parse bytes itself.

## Docstring contract
- **Layer:** 2
- **Depends on:** `Mode` (Layer 0 type)
- **Implements:** `enforce(declared_mode: Mode, required_mode: Mode, parsed_components) -> None` — raises/rejects on mismatch, otherwise returns normally
- **Outside:** Parsing wire bytes (`signature_wire_format.py`); verifying the actual signature components (`signature_combiner.py`, via the underlying `Verifier`s)
- **Inside:** The mode cross-check itself, and only that
- **Security notes:** Implements SR-1 in full

## Required behavior
- `required_mode` is passed in from the server-side construction context — this function never reads it from anything wire-derived (FR-2.3, SR-1).
- `declared_mode` (from the wire) is used **only** to know how many components were parsed — it plays no role in deciding acceptance.
- Mismatch between `declared_mode`-implied shape and `required_mode` → reject unconditionally, before `signature_combiner.py` calls into any `Verifier`.

## Inputs / outputs
- **In:** `declared_mode: Mode`, `required_mode: Mode`, parsed component count/shape from `signature_wire_format.py`.
- **Out:** Either silently returns (proceed to verification) or raises/signals rejection — never a partial pass.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client declares a mode that doesn't match `required_mode` → rejected unconditionally before any cryptographic verification runs.
- PQC component stripped from a real hybrid signature, declared-mode byte rewritten → this is exactly the shape mismatch this function must catch, before `signature_combiner.py` ever calls `verify()`.

## Security notes
- **SR-1** — this file's entire reason for existing.

## Mandatory tests this must pass
- `tests/signature/test_signature_combiner.py` (integration-level, via the combiner)
- `tests/security/test_sr_01_hybrid_downgrade_rejected.py` — strip the PQC component, rewrite the mode byte, confirm rejection happens here, before verification.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Actually verifying any signature — that's `signature_combiner.py` calling into Layer-1 `Verifier`s, after this function has already passed.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `14-directory-structure.md`
