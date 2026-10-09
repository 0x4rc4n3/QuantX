# `signature_combiner.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (Signature) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`'s review gates).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/signature_combiner.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
The single, generic `SignatureCombiner` class in the entire system (FR-2.1) — orchestrates parsing wire bytes, cross-checking the declared mode against the server's `required_mode`, and calling into the underlying `Verifier`(s) for the components a given mode requires. Algorithm pairing is constructor-time wiring, never a new class (P3).

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/signature/`
- **Depends on:** `quantx_core.interfaces.verifier.Verifier` (Layer 0, one or two instances wired in per the pairing); `quantx_core.types.mode.Mode` (Layer 0); `signature_wire_format.py` (parsing only — this file never parses bytes itself); `signature_mode_enforcement.py` (the mode cross-check — isolated so it can be reviewed without also holding wire-parsing/orchestration logic in view)
- **Imported by:** `algorithm_registry.py` (Layer 3) wires a configured instance per registry role; `challenge_issuer.py`/`session_orchestrator.py` (Layer 4) call it during `finish()`

## Docstring contract
- **Layer:** 2
- **Depends on:** `Verifier` (Layer 0), `Mode` (Layer 0), `signature_wire_format.py`, `signature_mode_enforcement.py`
- **Implements:** `verify(wire_bytes: bytes) -> bool` — parses, enforces mode, then verifies
- **Outside:** Wire encoding/decoding itself (`signature_wire_format.py`); the mode cross-check logic itself (`signature_mode_enforcement.py`) — this file calls both, holds neither's internals.
- **Inside:** Orchestration: parse → enforce mode → verify each required component → combine into one boolean result.
- **Security notes:** Implements FR-2.3/SR-1 by delegating the actual mode check to `signature_mode_enforcement.py` and never proceeding to verification before that check passes.

## Required behavior
- Exactly one `SignatureCombiner` class exists in the system (FR-2.1) — a different pairing (e.g. Ed25519+ML-DSA-65 vs. ECDSA-P256+ML-DSA-87) is a different constructor call, never a new class or an `if family ==` branch (P2, P3).
- `required_mode` is fixed at construction time by the server and is never read from wire data to decide acceptance (FR-2.3, SR-1) — the wire-declared mode from `signature_wire_format.py` is used only to know the parsed shape, then cross-checked via `signature_mode_enforcement.py` before any `Verifier.verify()` call executes.
- On mode mismatch, rejects unconditionally, before any cryptographic verification runs (FR-2.3, SR-1) — the rejection happens inside `signature_mode_enforcement.py`; this file's job is simply to call it first, unconditionally, before touching any `Verifier`.
- For a genuine `HYBRID` signature, calls `verify()` on both the classical and PQC `Verifier` and requires both to return `True` (normative: `docs/QUANTX-V2-ARCHITECTURE.md` §8 — AND for `HYBRID`, exactly one component for single modes, same canonicalized message to every verifier). Every component signs and verifies the D-009 payload: `QuantX-SIG-v1` prefix, mode, role and length-prefixed message (see `docs/DECISIONS.md` D-009). ML-DSA `context=None`.
- Overall result is `False` on any internal exception — this class inherits `Verifier`-style fail-closed behavior at the orchestration level (FR-0.1's spirit, applied to the composite).

## Inputs / outputs
- **In:** raw wire bytes (as produced by `signature_wire_format.py`'s encode side, or received over the wire).
- **Out:** `bool` — `True` only if mode matches `required_mode` **and** every required component verifies; `False` otherwise, never raises.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client declares a mode that doesn't match server `required_mode` → rejected unconditionally before any cryptographic verification runs (SR-1, `13-error-and-edge-cases.md`).
- PQC component stripped from a real hybrid signature, declared-mode byte rewritten → caught by `signature_mode_enforcement.py` before this class calls any `Verifier` (the hybrid-downgrade test, mandatory test 1, `10-security-requirements.md`).
- A length-prefixed field claims a length larger than the remaining buffer → rejected as malformed input by `signature_wire_format.py`'s parser, surfaced here as a fail-closed `False`, never an out-of-bounds read.

## Security notes
- **SR-1 (via delegation).** This class's entire security posture rests on never calling a `Verifier` before `signature_mode_enforcement.py` has passed — the actual SR-1 logic lives there, not here, by design (`14-directory-structure.md`'s stated reason for the split).
- This is a `GATE_REVIEW_REQUIRED` component per `10-security-requirements.md`'s review-gates list (`SignatureCombiner`, `KEMCombiner` named explicitly).

## Mandatory tests this must pass
- `tests/signature/test_signature_combiner.py`
- `tests/security/test_sr_01_hybrid_downgrade_rejected.py`
- `tests/security/test_signature_wire_format_fuzz.py` (indirectly, via the parser this class calls)

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P2.** One algorithm per adapter file, forever.
- **P3.** Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Wire encoding/decoding — `signature_wire_format.py`.
- The mode cross-check logic itself — `signature_mode_enforcement.py`.
- Choosing which algorithms are paired — that's `AlgorithmRegistry` (Layer 3) at construction time.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `14-directory-structure.md`, `02-build-order.md`
