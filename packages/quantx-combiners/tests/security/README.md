# `quantx-combiners/tests/security/`

## What this is
The highest-scrutiny security tests in the whole tree: SR-1 (hybrid downgrade), SR-7 (KEM substitution), and both mandatory wire-parser fuzz suites.

## Part of
`quantx-combiners`, Layer 2.

## Contains
- `test_sr_01_hybrid_downgrade_rejected.py` — SR-1
- `test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py` — SR-7
- `test_signature_wire_format_fuzz.py` — mandatory test 5 (Hypothesis)
- `test_kem_wire_format_fuzz.py` — mandatory test 5 (Hypothesis)

## Why divided this way
Named `test_sr_<NN>_<slug>.py` per `14-directory-structure.md`'s convention, except the two fuzz suites, which verify a mandatory test *category* rather than a single numbered SR item, per that same doc's stated exception.

## Dependency rules
- `test_sr_01_...` depends on `signature_combiner.py` + `signature_mode_enforcement.py`.
- `test_sr_07_...` depends on `kem_combiner.py` + `kem_hkdf_binding.py`.
- The two fuzz suites depend on their respective `*_wire_format.py` parsers only.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
