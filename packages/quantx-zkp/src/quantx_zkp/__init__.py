"""QuantX zero-knowledge and group membership proofs package.

Layer: 9
Depends on: quantx_zkp.anonymous_proof_backend, quantx_zkp.merkle_membership_proof, quantx_zkp.merkle_tree
Implements: Package exports for Merkle membership and anonymous proof interfaces
Outside: Relying party validation and session orchestrator gates
Inside: Merkle tree construction, path verifier, and audited anonymous interface placeholder
Security notes: Merkle proofs are sound but non-anonymous (FR-9.3); verifier actually walks path to root (SR-2).
"""

from __future__ import annotations

from quantx_zkp.anonymous_proof_backend import AnonymousProofBackend
from quantx_zkp.merkle_membership_proof import MerkleMembershipProof
from quantx_zkp.merkle_tree import MerkleProofStep, MerkleTree

__all__ = [
    "AnonymousProofBackend",
    "MerkleMembershipProof",
    "MerkleProofStep",
    "MerkleTree",
]
