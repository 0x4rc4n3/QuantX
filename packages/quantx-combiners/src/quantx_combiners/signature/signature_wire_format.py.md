# `signature_wire_format.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (Signature) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Encodes/decodes the length-prefixed binary wire format a hybrid/PQC-only/classical-only signature is transmitted as. Pure plumbing — deliberately holds no mode-enforcement or verification logic, so the security-critical code in `signature_mode_enforcement.py` and `signature_combiner.py` never has to be read alongside byte-parsing details (`14-directory-structure.md`).

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/signature/`
- **Depends on:** `quantx_core.types.mode.Mode` (Layer 0) — to tag the parsed shape; `quantx_core.exceptions.malformed_input_error.MalformedInputError` (Layer 0)
- **Imported by:** `signature_combiner.py` (parsing only — never calls into `signature_mode_enforcement.py` or any `Verifier` itself)

## Docstring contract
- **Layer:** 2
- **Depends on:** `Mode`, `MalformedInputError` (Layer 0)
- **Implements:** `encode(mode, components) -> bytes`; `decode(wire_bytes) -> (declared_mode, parsed_components)`
- **Outside:** Deciding whether the parsed `declared_mode` is acceptable — that's `signature_mode_enforcement.py`'s job entirely; this file has no opinion on acceptance.
- **Inside:** Length-prefixed binary framing: reading/writing each component's declared length and bytes.
- **Wire format:** Versioned length-prefixed binary defined normatively in `docs/QUANTX-V2-ARCHITECTURE.md` §5: version byte, mode byte, component count, and ordered algorithm-ID/signature components with bounded big-endian lengths. Unknown versions, malformed lengths, duplicate algorithms, invalid UTF-8, mode/count mismatches, and trailing bytes are rejected.
- **Security notes:** Carries no acceptance-decision authority by design — parses shape only.

## Required behavior
- `decode()` reads the mode tag and each length-prefixed component without judging whether the result is acceptable — that judgment belongs entirely to `signature_mode_enforcement.py`.
- Every length field is bounds-checked against the remaining buffer before use — a length claiming more bytes than remain is rejected as malformed input, never read past the buffer end (`13-error-and-edge-cases.md`).
- On any malformed/truncated input, raises `MalformedInputError` (or an equivalent internally-caught signal) rather than allowing a parse to silently under-read or over-read.
- `encode()` is the exact inverse of `decode()` for any value `decode()` would accept.

## Inputs / outputs
- **In:** `encode`: a `Mode` plus the raw component bytes for that mode's required algorithms. `decode`: raw wire bytes.
- **Out:** `encode`: length-prefixed wire bytes. `decode`: `(declared_mode, parsed_components)` or a raised/caught malformed-input signal.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A length-prefixed field claims a length larger than the remaining buffer → rejected as malformed input by this same fuzz-tested parser path — never an out-of-bounds read (`13-error-and-edge-cases.md`).
- Signature bytes are malformed or truncated → this is where that failure is first caught, then surfaced up through `signature_combiner.py` as a fail-closed `False` (FR-0.1's spirit).

## Security notes
- **Mandatory test 5 (wire-parser fuzzing, `10-security-requirements.md`).** This file is a primary fuzz target — property-based tests (Hypothesis) throw malformed and adversarially-sized length fields at `decode()`.
- **Not `GATE_REVIEW_REQUIRED`.** `BUILD_PROMPT.md` §5 explicitly excludes this file from the gate-review notice — `14-directory-structure.md` splits wire-format plumbing out specifically so it isn't mixed with the security-critical logic that *is* gated.

## Mandatory tests this must pass
- `tests/signature/test_signature_wire_format.py`
- `tests/security/test_signature_wire_format_fuzz.py`

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any decision about whether a parsed mode is acceptable — `signature_mode_enforcement.py`.
- Calling any `Verifier` — `signature_combiner.py`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
