# `test_merkle_tree.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `MerkleTree.build()` produces a correct root and correct sibling-hash paths for a sample member set.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `tests/`
- **Depends on:** `merkle_tree.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 9
- **Depends on:** `merkle_tree.py`
- **Implements:** pytest test functions.
- **Outside:** Path verification — `test_merkle_membership_proof.py`.
- **Inside:** Tree construction correctness.
- **Security notes:** None — construction correctness only.

## Required behavior
- Root is deterministic for a given member set.
- The sibling-hash path produced for a given member, when walked manually, reproduces the tree's actual root.

## Inputs / outputs
- **In:** a sample member set.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `merkle_tree.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Path verification logic — separate file.

## Source docs
`04-functional-requirements.md`
