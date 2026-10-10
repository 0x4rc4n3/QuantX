"""Merkle membership proof verifier that walks authentication paths to the root.

Layer: 9
Depends on: quantx_zkp.merkle_tree.MerkleProofStep, quantx_zkp.merkle_tree.hash_leaf, quantx_zkp.merkle_tree.hash_node
Implements: MerkleMembershipProof
Outside: Tree construction and leaf storage (merkle_tree.py)
Inside: Recomputing Merkle root by walking authentication path from leaf to root
Security notes: SR-2 in full: verifier actually walks the path to the root; lookup-table stubs fail. Non-anonymity caveat: proves group membership only, not unlinkability (FR-9.3).
"""

from __future__ import annotations

import hmac
from typing import Sequence

from quantx_zkp.merkle_tree import MerkleProofStep, hash_leaf, hash_node

GATE_REVIEW_REQUIRED: bool = True


class MerkleMembershipProof:
    """Verifies cryptographic group membership by walking sibling paths to the Merkle root.

    CAVEAT (FR-9.3): Merkle membership proofs are sound and verifiable, but they are NON-ANONYMOUS.
    They prove inclusion in a group; they do not provide zero-knowledge unlinkability.
    """

    @staticmethod
    def verify(
        member: bytes,
        path: Sequence[MerkleProofStep],
        claimed_root: bytes,
    ) -> bool:
        """Verify membership by walking the authentication path up to claimed_root (SR-2).

        Returns True if and only if hashing member with the sibling path yields claimed_root.
        """
        if not member or not claimed_root:
            return False

        current = hash_leaf(member)
        for step in path:
            if step.is_right:
                current = hash_node(current, step.sibling_hash)
            else:
                current = hash_node(step.sibling_hash, current)

        return hmac.compare_digest(current, claimed_root)
