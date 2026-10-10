"""Shared test fixtures for quantx-zkp test suite.

Layer: 9
Depends on: quantx_zkp.merkle_tree.MerkleTree
Implements: Pytest fixtures for Merkle tree and member samples
Outside: Test assertion logic
Inside: Fixture provisioning for unit and security suites
Security notes: Fixtures for testing sound Merkle proof verification (SR-02).
"""

from __future__ import annotations

import pytest
from quantx_zkp.merkle_tree import MerkleTree


@pytest.fixture
def sample_members() -> list[bytes]:
    return [
        b"alice@example.com",
        b"bob@example.com",
        b"carol@example.com",
        b"david@example.com",
        b"eve@example.com",
    ]


@pytest.fixture
def merkle_tree(sample_members: list[bytes]) -> MerkleTree:
    return MerkleTree.build(sample_members)
