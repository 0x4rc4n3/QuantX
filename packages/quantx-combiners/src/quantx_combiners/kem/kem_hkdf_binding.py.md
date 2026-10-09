# `kem_hkdf_binding.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners (KEM) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-7).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/kem_combiner.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Isolates the one computation that makes KEM ciphertext/public-key substitution cryptographically detectable rather than merely policy-detectable: binding both values into the HKDF `info` parameter before deriving the shared secret (FR-2.4, SR-7). Split out of `kem_combiner.py` for the same reason `signature_mode_enforcement.py` is split from `signature_combiner.py` — so this specific security property can be reviewed in isolation.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `src/quantx_combiners/kem/`
- **Depends on:** A standard HKDF implementation from `cryptography` (pyca) — no hand-rolled KDF (D1).
- **Imported by:** `kem_combiner.py` only.
- **Sideways-import note:** Nothing from `kem_wire_format.py` — this file receives already-parsed ciphertext/public-key bytes, it doesn't parse the wire format itself.

## Docstring contract
- **Layer:** 2
- **Depends on:** `cryptography`'s HKDF implementation (no in-house KDF, D1)
- **Implements:** `derive(shared_secrets, ciphertexts, public_keys) -> bytes` — HKDF with ciphertext(s) and public key(s) folded into `info`
- **Outside:** Wire parsing (`kem_wire_format.py`); orchestrating which `KEMProvider`s ran (`kem_combiner.py`).
- **Inside:** The HKDF `info`-binding construction itself, and only that.
- **Security notes:** Implements SR-7 in full.

## Required behavior
- Both the KEM ciphertext and the public key used for encapsulation are bound into the HKDF `info` parameter (FR-2.4) — never appended to the payload or checked out-of-band, where substitution could go undetected by the crypto itself.
- A ciphertext or public-key substitution post-encapsulation changes the derived key deterministically, so decapsulation on the wrong pairing produces a shared secret that will not match downstream, rather than silently succeeding.
- Uses `cryptography`'s HKDF implementation — never a hand-rolled KDF (D1).

## Inputs / outputs
- **In:** the raw shared secret(s) from `KEMProvider.decapsulate()`, plus the ciphertext(s) and public key(s) involved.
- **Out:** the final derived key material, cryptographically bound to the specific ciphertext/public-key pairing used.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Client substitutes a different KEM ciphertext or public key post-encapsulation → detected — both are bound into the HKDF `info` parameter (SR-7, `13-error-and-edge-cases.md`).

## Security notes
- **SR-7** — this file's entire reason for existing.

## Mandatory tests this must pass
- `tests/kem/test_kem_combiner.py` (integration-level, via the combiner)
- `tests/security/test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py` — swap either value post-encapsulation, confirm the derived key changes / decapsulation fails.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Wire parsing — `kem_wire_format.py`.
- Calling `KEMProvider.decapsulate()` itself — `kem_combiner.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `14-directory-structure.md`
