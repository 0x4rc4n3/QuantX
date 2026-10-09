# `test_kem_combiner.py`

**Package:** `quantx-combiners` · **Layer:** 2 — Combiners · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `KEMCombiner`'s orchestration: correct derivation across HYBRID, PQC_ONLY, and CLASSICAL_ONLY modes, using genuine (non-adversarial) inputs.

## Part of / dependency graph
- **Package:** `quantx-combiners`, `tests/`
- **Depends on:** `kem_combiner.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 2
- **Depends on:** `kem_combiner.py`
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- A genuine encapsulate/decapsulate round trip under each mode derives a matching shared secret on both sides.
- Confirms `kem_hkdf_binding.py` is actually invoked with the real ciphertext/public key — the adversarial substitution scenario itself is `test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py`'s job.

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the integration test for `kem_combiner.py`'s non-adversarial behavior.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside this file's named subject.

## Source docs
`04-functional-requirements.md`
