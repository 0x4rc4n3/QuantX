# `quantx-zkp` — `tests/`

## What this is
The test suite for Layer 9: Merkle construction/verification and the SR-2 security test, plus confirming the anonymous-proof placeholder genuinely raises `NotImplementedError`.

## Part of
`quantx-zkp`, Layer 9.

## Contains
- `conftest.py`
- `test_merkle_tree.py`, `test_merkle_membership_proof.py`
- `test_anonymous_proof_backend_raises_not_implemented.py`
- `security/` — SR-2

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- Each test file depends on the one `src/` file it names plus shared fixtures.

## Source docs
`14-directory-structure.md`
