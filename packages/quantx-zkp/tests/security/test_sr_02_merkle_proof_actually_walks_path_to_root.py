"""Mandatory security test SR-02: Merkle verifier actually walks path to root.

Layer: 9
Depends on: quantx_zkp.merkle_membership_proof.MerkleMembershipProof, quantx_zkp.merkle_tree.MerkleTree
Implements: SR-02 mandatory test verifying that proof verification computes the path to the root
Outside: General structural verification
Inside: Cross-tree membership test defeating lookup-table shortcuts
Security notes: SR-2: A membership verifier must walk the path to root; lookup-table shortcuts fail. Non-anonymity caveat applies (FR-9.3).
"""

from __future__ import annotations

from quantx_zkp.merkle_membership_proof import MerkleMembershipProof
from quantx_zkp.merkle_tree import MerkleTree


def test_sr_02_merkle_proof_actually_walks_path_to_root() -> None:
    # Tree A: legitimate group A
    tree_a_members = [
        b"alice@corp.internal",
        b"bob@corp.internal",
        b"carol@corp.internal",
    ]
    tree_a = MerkleTree.build(tree_a_members)

    # Tree B: different group B with a different root
    tree_b_members = [
        b"dave@other.org",
        b"eve@other.org",
        b"frank@other.org",
    ]
    tree_b = MerkleTree.build(tree_b_members)

    # Alice is a legitimate member of Tree A
    proof_a = tree_a.proof_for(b"alice@corp.internal")

    # 1. Genuine verification against Tree A root succeeds
    assert (
        MerkleMembershipProof.verify(
            member=b"alice@corp.internal",
            path=proof_a,
            claimed_root=tree_a.root,
        )
        is True
    )

    # 2. Adversarial attempt: present Alice's proof against Tree B's root.
    # A naive stub that merely looks up whether "alice@corp.internal" exists in an in-memory set
    # or table might mistakenly return True. A path-walking verifier (SR-2) MUST compute
    # the candidate root from Alice + proof_a and fail because it does not equal tree_b.root.
    assert (
        MerkleMembershipProof.verify(
            member=b"alice@corp.internal",
            path=proof_a,
            claimed_root=tree_b.root,
        )
        is False
    )

    # 3. Present Dave's proof from Tree B against Tree A's root
    proof_b = tree_b.proof_for(b"dave@other.org")
    assert (
        MerkleMembershipProof.verify(
            member=b"dave@other.org",
            path=proof_b,
            claimed_root=tree_a.root,
        )
        is False
    )
