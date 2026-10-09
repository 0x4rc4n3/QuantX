# `kem_combiner.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (KEM) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`'s review gates).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/kem_combiner.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
The single, generic `KEMCombiner` class in the entire system (FR-2.2) — orchestrates parsing wire bytes and combining one or two `KEMProvider` encapsulations (classical + PQC, per mode) into one shared secret, binding ciphertext and public key into the HKDF `info` parameter so substitution is cryptographically detectable (FR-2.4, SR-7).

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/kem/`
- **Depends on:** `quantx_core.interfaces.kem_provider.KEMProvider` (Layer 0, one or two instances wired in per the pairing); `quantx_core.types.mode.Mode` (Layer 0); `kem_wire_format.py` (parsing only); `kem_hkdf_binding.py` (the ciphertext/public-key → HKDF `info` binding, isolated per SR-7)
- **Imported by:** `algorithm_registry.py` (Layer 3) wires a configured instance per registry role

## Docstring contract
- **Layer:** 2
- **Depends on:** `KEMProvider` (Layer 0), `Mode` (Layer 0), `kem_wire_format.py`, `kem_hkdf_binding.py`
- **Implements:** `combine(wire_bytes: bytes) -> bytes` (derived shared secret) or an equivalent encapsulate/decapsulate-combining pair
- **Outside:** Wire encoding/decoding itself; the HKDF-binding computation itself.
- **Inside:** Orchestration: parse → decapsulate each required component → derive the combined shared secret via `kem_hkdf_binding.py`.
- **Security notes:** Implements FR-2.4/SR-7 by delegating the actual binding computation to `kem_hkdf_binding.py`.

## Required behavior
- Exactly one `KEMCombiner` class exists (FR-2.2) — pairing is constructor-time wiring, never a new class (P3).
- For `HYBRID` mode, decapsulates via both the classical and PQC `KEMProvider` and combines both resulting shared secrets through `kem_hkdf_binding.py`'s HKDF derivation (normative: `docs/QUANTX-V2-ARCHITECTURE.md` §7 — HKDF-SHA256, `length=32`, `salt=None`, IKM is the concatenation of the shared secrets in registry order, `info` is the exact byte construction in §7; still `GATE_REVIEW_REQUIRED`).
- Ciphertext and public key are bound into the HKDF `info` parameter, not the payload, so substitution changes the derived key rather than silently succeeding (FR-2.4, SR-7).
- Mode handling mirrors `signature_combiner.py`'s discipline even though the specific SR-1 mode-mismatch scenario is a signature-side concern — a KEM-side mode mismatch (wrong number of components for the declared mode) is still rejected via the wire-format parser's shape check before combination proceeds.

## Inputs / outputs
- **In:** raw wire bytes containing one or two KEM ciphertexts, depending on mode.
- **Out:** the combined/derived shared secret, or a fail-closed rejection on malformed/substituted input.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client substitutes a different KEM ciphertext or public key post-encapsulation → detected — both are bound into the HKDF `info` parameter (SR-7, `13-error-and-edge-cases.md`).
- A length-prefixed field claims a length larger than the remaining buffer → rejected as malformed input by `kem_wire_format.py`'s parser.

## Security notes
- **SR-7 (via delegation).** The actual binding computation lives in `kem_hkdf_binding.py`; this file's job is to call it with the correct ciphertext/public-key pair every time, never skipping it.
- This is a `GATE_REVIEW_REQUIRED` component per `10-security-requirements.md`'s review-gates list.

## Mandatory tests this must pass
- `tests/kem/test_kem_combiner.py`
- `tests/security/test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py`
- `tests/security/test_kem_wire_format_fuzz.py` (indirectly, via the parser this class calls)

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P2.** One algorithm per adapter file, forever.
- **P3.** Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Wire encoding/decoding — `kem_wire_format.py`.
- The HKDF-binding computation itself — `kem_hkdf_binding.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `14-directory-structure.md`
