# `test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The mandatory KEM ciphertext/public-key substitution test (mandatory test 4, `10-security-requirements.md`): swap either value post-encapsulation — must fail, because both are bound into the HKDF `info` parameter.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/security/`
- **Depends on:** `kem_combiner.py`; `kem_hkdf_binding.py`; `kem_wire_format.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 2
- **Depends on:** The full KEM-combining path.
- **Implements:** The mandatory automated security test for SR-7.
- **Outside:** SR-1 (that's the signature-side test).
- **Inside:** A genuine encapsulate/decapsulate round trip, then swapping the ciphertext or public key before decapsulation.
- **Security notes:** This file **is** the SR-7 enforcement check.

## Required behavior
- Perform a genuine encapsulation producing `(ciphertext, shared_secret)` for a real public key.
- Swap in a different, validly-formed ciphertext (from a different encapsulation) before decapsulation, and separately, swap in a different public key — confirm both cases either fail decapsulation outright or produce a shared secret that does not match the honest path's, because both values are bound into HKDF `info`.

## Inputs / outputs
- **In:** substituted ciphertext/public-key pairs.
- **Out:** must not silently succeed with a matching shared secret.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client substitutes a different KEM ciphertext or public key post-encapsulation → detected (SR-7, `13-error-and-edge-cases.md`).

## Security notes
- **SR-7.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-7 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- SR-1 (hybrid downgrade) — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
