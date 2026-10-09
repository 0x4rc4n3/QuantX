# `kem_wire_format.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (KEM) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Encodes/decodes the length-prefixed binary wire format one or two KEM ciphertexts are transmitted as. Pure plumbing, deliberately separated from `kem_hkdf_binding.py`'s security-critical binding logic (`14-directory-structure.md`).

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/kem/`
- **Depends on:** `quantx_core.types.mode.Mode` (Layer 0); `quantx_core.exceptions.malformed_input_error.MalformedInputError` (Layer 0)
- **Imported by:** `kem_combiner.py` (parsing only — never calls `kem_hkdf_binding.py` or any `KEMProvider` itself)

## Docstring contract
- **Layer:** 2
- **Depends on:** `Mode`, `MalformedInputError` (Layer 0)
- **Implements:** `encode(mode, components) -> bytes`; `decode(wire_bytes) -> (declared_mode, parsed_components)`, where each component contains `algorithm_id`, `public_key`, and `ciphertext`.
- **Outside:** The HKDF binding computation — `kem_hkdf_binding.py`'s job entirely.
- **Inside:** Length-prefixed binary framing for one or two ordered KEM components, each containing an algorithm identifier, public key, and ciphertext.
- **Wire format:** Versioned length-prefixed binary defined normatively in `docs/QUANTX-V2-ARCHITECTURE.md` §6: version byte, mode byte, component count, and ordered algorithm-ID/public-key/ciphertext components with bounded big-endian lengths. Unknown versions, malformed lengths, duplicate algorithms, invalid UTF-8, mode/count mismatches, and trailing bytes are rejected.
- **Security notes:** Carries no acceptance-decision or binding authority by design.

## Required behavior
- `decode()` reads the mode tag and each length-prefixed ciphertext without performing any HKDF binding — that's `kem_hkdf_binding.py`'s job entirely.
- Every length field is bounds-checked against the remaining buffer before use.
- On any malformed/truncated input, raises/signals `MalformedInputError` rather than reading past the buffer end.

## Inputs / outputs
- **In:** `encode`: a `Mode` plus one or two ordered `(algorithm_id, public_key, ciphertext)` components. `decode`: raw wire bytes.
- **Out:** `encode`: versioned length-prefixed wire bytes. `decode`: `(declared_mode, parsed_components)` or a raised/caught malformed-input signal.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A length-prefixed field claims a length larger than the remaining buffer → rejected as malformed input, never an out-of-bounds read (`13-error-and-edge-cases.md`).

## Security notes
- **Mandatory test 5 (wire-parser fuzzing).** A primary fuzz target alongside `signature_wire_format.py`.
- **Not `GATE_REVIEW_REQUIRED`** — plumbing, per `BUILD_PROMPT.md` §5's explicit exclusion.

## Mandatory tests this must pass
- `tests/kem/test_kem_wire_format.py`
- `tests/security/test_kem_wire_format_fuzz.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- The HKDF binding computation — `kem_hkdf_binding.py`.
- Calling any `KEMProvider` — `kem_combiner.py`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
