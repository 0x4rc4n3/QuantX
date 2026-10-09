# `quantx-zkp/tests/security/`

## What this is
Layer 9's one dedicated security test: SR-2, the verifier must actually walk the membership path to the root.

## Part of
`quantx-zkp`, Layer 9.

## Contains
- `test_sr_02_merkle_proof_actually_walks_path_to_root.py`

## Why divided this way
Named `test_sr_<NN>_*` per `14-directory-structure.md`'s convention.

## Dependency rules
- Depends on `merkle_membership_proof.py` and `merkle_tree.py`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
