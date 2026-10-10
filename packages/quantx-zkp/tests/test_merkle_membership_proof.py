"""Unit tests for MerkleMembershipProof verification.

Layer: 9
Depends on: quantx_zkp.merkle_membership_proof.MerkleMembershipProof, quantx_zkp.merkle_tree.MerkleProofStep, quantx_zkp.merkle_tree.MerkleTree
Implements: Pytest tests validating genuine acceptance and tampered proof rejection
Outside: SR-2 specific lookup-table stub detection (tested in security suite)
Inside: Authentic path verification, tampered sibling hash rejection, and empty inputs handling
Security notes: Confirms that genuine proofs verify and corrupted paths fail. Non-anonymity caveat applies (FR-9.3).
"""

from __future__ import annotations

from quantx_zkp.merkle_membership_proof import MerkleMembershipProof
from quantx_zkp.merkle_tree import MerkleProofStep, MerkleTree


def test_merkle_membership_proof_genuine_success(
    merkle_tree: MerkleTree,
    sample_members: list[bytes],
) -> None:
    for member in sample_members:
        proof = merkle_tree.proof_for(member)
        valid = MerkleMembershipProof.verify(
            member=member,
            path=proof,
            claimed_root=merkle_tree.root,
        )
        assert valid is True


def test_merkle_membership_proof_tampered_sibling_fails(
    merkle_tree: MerkleTree,
    sample_members: list[bytes],
) -> None:
    member = sample_members[0]
    proof = merkle_tree.proof_for(member)
    assert len(proof) > 0

    # Tamper with first sibling hash in path
    tampered_step = MerkleProofStep(
        sibling_hash=b"\xff" * 32,
        is_right=proof[0].is_right,
    )
    tampered_proof = [tampered_step] + list(proof[1:])

    valid = MerkleMembershipProof.verify(
        member=member,
        path=tampered_proof,
        claimed_root=merkle_tree.root,
    )
    assert valid is False


def test_merkle_membership_proof_empty_or_wrong_root_fails(
    merkle_tree: MerkleTree,
    sample_members: list[bytes],
) -> None:
    member = sample_members[0]
    proof = merkle_tree.proof_for(member)

    assert MerkleMembershipProof.verify(member, proof, b"\x00" * 32) is False
    assert MerkleMembershipProof.verify(b"", proof, merkle_tree.root) is False
    assert MerkleMembershipProof.verify(member, proof, b"") is False
