# `merkle_tree.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A standard Merkle tree construction over a set of members — leaves, internal nodes, and root computation — the data structure `merkle_membership_proof.py` walks paths through.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `src/quantx_zkp`
- **Depends on:** SHA-256 from the standard library `hashlib` (D-015).
- **Imported by:** `merkle_membership_proof.py` (this package)

## Docstring contract
- **Layer:** 9
- **Depends on:** A standard cryptographic hash function.
- **Implements:** `build(members) -> MerkleTree`; `.root`; `.proof_for(member) -> list[bytes]` (sibling hashes along the path to root)
- **Outside:** Verifying a proof against a claimed root — `merkle_membership_proof.py`'s job.
- **Inside:** Tree construction, root computation, and path extraction for a given member.
- **Security notes:** No `SR-x` item is specific to construction itself — SR-2 concerns the *verifier* actually walking the path, which is `merkle_membership_proof.py`'s responsibility, not this file's.

## Required behavior
- Builds a Merkle tree over a set of members and computes the root.
- Produces the sibling-hash path from a given leaf to the root, for `merkle_membership_proof.py` to package as a proof.

## Inputs / outputs
- **In:** a set of members (leaves).
- **Out:** a tree with a computable root and, per member, a path of sibling hashes to that root.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Leaf and node hashes use distinct one-byte prefixes (`0x00` leaf, `0x01` node); an odd node is promoted without duplicating the last leaf (D-015). Vectors are required.

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- `tests/test_merkle_tree.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Verifying a proof — `merkle_membership_proof.py`.

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`
