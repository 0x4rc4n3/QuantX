# `quantx_zkp` — package source root

## What this is
Layer 9: Merkle-tree group-membership proofs (real, working, honestly scoped as non-anonymous) and the placeholder for true anonymous proofs (deliberately unimplemented, D9).

## Part of
`quantx-zkp`, Layer 9. `merkle_membership_proof.py` and `anonymous_proof_backend.py` are both `GATE_REVIEW_REQUIRED`.

## Contains
- `merkle_tree.py` — tree construction
- `merkle_membership_proof.py` — the verifier that must actually walk the path (SR-2)
- `anonymous_proof_backend.py` — `NotImplementedError` until funded, scoped external audit (D9)

## Why divided this way
Tree construction and path-verification are split so SR-2's specific, safety-critical property ("actually walks the path") lives in one small, reviewable file, per `14-directory-structure.md`.

## Dependency rules
- `merkle_membership_proof.py` depends on `merkle_tree.py`.
- `anonymous_proof_backend.py` depends on nothing — it's deliberately unimplemented, not a wrapper around the Merkle construction.

## Source docs
`04-functional-requirements.md`, `00-index.md`, `14-directory-structure.md`
