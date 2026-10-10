"""Unit tests for MerkleTree construction and path extraction.

Layer: 9
Depends on: quantx_zkp.merkle_tree.MerkleTree, quantx_zkp.merkle_tree.hash_leaf, quantx_zkp.merkle_tree.hash_node
Implements: Pytest tests validating deterministic Merkle root and sibling paths
Outside: Proof verification interface
Inside: Root computation, odd-node promotion (D-015), and authentication path extraction
Security notes: Tree construction validation; non-anonymity caveat applies (FR-9.3).
"""

from __future__ import annotations

import pytest
from quantx_zkp.merkle_tree import MerkleTree, hash_leaf, hash_node


def test_merkle_tree_deterministic_root(sample_members: list[bytes]) -> None:
    tree1 = MerkleTree.build(sample_members)
    tree2 = MerkleTree.build(sample_members)
    assert tree1.root == tree2.root
    assert len(tree1.root) == 32


def test_merkle_tree_path_reproduces_root(
    merkle_tree: MerkleTree,
    sample_members: list[bytes],
) -> None:
    for member in sample_members:
        proof = merkle_tree.proof_for(member)
        current = hash_leaf(member)
        for step in proof:
            if step.is_right:
                current = hash_node(current, step.sibling_hash)
            else:
                current = hash_node(step.sibling_hash, current)
        assert current == merkle_tree.root


def test_merkle_tree_unknown_member_raises(merkle_tree: MerkleTree) -> None:
    with pytest.raises(ValueError, match="not found in Merkle tree"):
        merkle_tree.proof_for(b"stranger@example.com")


def test_merkle_tree_empty_members_raises() -> None:
    with pytest.raises(ValueError, match="empty members"):
        MerkleTree.build([])
