"""Standard Merkle tree construction with domain separation and odd-node promotion.

Layer: 9
Depends on: hashlib.sha256
Implements: MerkleTree and MerkleProofStep
Outside: Verifying a proof against a claimed root (merkle_membership_proof.py)
Inside: Tree construction, root computation, and sibling-hash path extraction
Security notes: Proves sound group membership but is non-anonymous (FR-9.3). Domain separation: 0x00 leaf prefix, 0x01 node prefix; odd nodes promoted without duplicate leaf creation (D-015).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Sequence

LEAF_PREFIX: bytes = b"\x00"
NODE_PREFIX: bytes = b"\x01"


def hash_leaf(data: bytes) -> bytes:
    """Compute domain-separated leaf hash: SHA256(0x00 || data) (D-015)."""
    return hashlib.sha256(LEAF_PREFIX + data).digest()


def hash_node(left: bytes, right: bytes) -> bytes:
    """Compute domain-separated internal node hash: SHA256(0x01 || left || right) (D-015)."""
    return hashlib.sha256(NODE_PREFIX + left + right).digest()


@dataclass(frozen=True)
class MerkleProofStep:
    """One step along a Merkle authentication path to the root."""

    sibling_hash: bytes
    is_right: bool  # True if sibling is to the right of current node, False if to the left


class MerkleTree:
    """Immutable Merkle tree constructed over a set of member leaves."""

    def __init__(self, members: Sequence[bytes], levels: list[list[bytes]]) -> None:
        self._members = tuple(members)
        self._levels = levels
        self._root = levels[-1][0] if levels and levels[-1] else b""

    @classmethod
    def build(cls, members: Sequence[bytes]) -> MerkleTree:
        """Build Merkle tree from member leaves with D-015 odd-node promotion."""
        if not members:
            raise ValueError("Cannot build Merkle tree over empty members")

        # Level 0: leaf hashes
        current_level: list[bytes] = [hash_leaf(m) for m in members]
        levels: list[list[bytes]] = [current_level]

        while len(current_level) > 1:
            next_level: list[bytes] = []
            n = len(current_level)
            for i in range(0, n - 1, 2):
                parent = hash_node(current_level[i], current_level[i + 1])
                next_level.append(parent)
            # Promote odd trailing node without duplicate leaf creation (D-015)
            if n % 2 == 1:
                next_level.append(current_level[-1])
            levels.append(next_level)
            current_level = next_level

        return cls(members=members, levels=levels)

    @property
    def root(self) -> bytes:
        """The 32-byte SHA-256 Merkle root hash."""
        return self._root

    @property
    def members(self) -> tuple[bytes, ...]:
        return self._members

    def proof_for(self, member: bytes) -> list[MerkleProofStep]:
        """Extract authentication path of sibling hashes from member leaf to root."""
        leaf_hash = hash_leaf(member)
        try:
            idx = self._levels[0].index(leaf_hash)
        except ValueError as exc:
            raise ValueError(f"Member '{member.hex()}' not found in Merkle tree") from exc

        proof: list[MerkleProofStep] = []
        for level in self._levels[:-1]:
            if idx % 2 == 0:
                # Node is on left; sibling is on right if exists
                if idx + 1 < len(level):
                    proof.append(MerkleProofStep(sibling_hash=level[idx + 1], is_right=True))
                # If odd trailing node promoted, no sibling at this level
            else:
                # Node is on right; sibling is on left
                proof.append(MerkleProofStep(sibling_hash=level[idx - 1], is_right=False))
            idx = idx // 2

        return proof
