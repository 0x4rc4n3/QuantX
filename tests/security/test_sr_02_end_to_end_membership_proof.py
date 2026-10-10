"""End-to-end security test for SR-2: Merkle membership proof verification walks path to root.

Layer: cross-cutting
Depends on: quantx_zkp.merkle_tree.MerkleTree, quantx_zkp.merkle_membership_proof.MerkleMembershipProof
Implements: Mandatory full-stack end-to-end test for SR-2 (proof verifier walks path to root)
Outside: Every other numbered SR item
Inside: Construct real MerkleTree with authentic members, extract proofs, and verify non-member/forged proofs are rejected end-to-end
Wire format: Native Merkle proof paths and root hashes
Security notes: Mandatory SR-2 end-to-end confirmation. Verifier must walk path to root and check it.
"""

from __future__ import annotations

from quantx_zkp.merkle_membership_proof import MerkleMembershipProof
from quantx_zkp.merkle_tree import MerkleProofStep, MerkleTree


def test_sr_02_end_to_end_membership_proof_walks_path_to_root() -> None:
    # 1. Build Merkle tree with real member IDs
    valid_members = [
        b"alice@corp.internal",
        b"bob@corp.internal",
        b"charlie@corp.internal",
        b"david@corp.internal",
    ]
    tree = MerkleTree.build(valid_members)
    root = tree.root

    # 2. Genuine member proof succeeds
    alice_path = tree.proof_for(b"alice@corp.internal")
    assert (
        MerkleMembershipProof.verify(
            member=b"alice@corp.internal",
            path=alice_path,
            claimed_root=root,
        )
        is True
    )

    # 3. Non-member attempting proof with Alice's path fails
    assert (
        MerkleMembershipProof.verify(
            member=b"eve@attacker.internal",
            path=alice_path,
            claimed_root=root,
        )
        is False
    )

    # 4. Tampered sibling path fails end-to-end
    tampered_path = list(alice_path)
    tampered_path[0] = MerkleProofStep(
        sibling_hash=b"\x00" * 32, is_right=tampered_path[0].is_right
    )
    assert (
        MerkleMembershipProof.verify(
            member=b"alice@corp.internal",
            path=tampered_path,
            claimed_root=root,
        )
        is False
    )
