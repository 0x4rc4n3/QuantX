"""Deliberately unimplemented placeholder for true anonymous ZK proofs.

Layer: 9
Depends on: Nothing
Implements: AnonymousProofBackend placeholder raising NotImplementedError
Outside: Sound Merkle-tree membership proofs (merkle_membership_proof.py)
Inside: Explicit NotImplementedError enforcement pending external cryptographic audit
Security notes: D9/FR-9.2: no homegrown zk-SNARK without a funded, scoped external audit.
"""

from __future__ import annotations

from typing import Any

GATE_REVIEW_REQUIRED: bool = True

AUDIT_PENDING_MESSAGE: str = (
    "Anonymous proof backend is deliberately unimplemented pending funded, scoped external audit "
    "(FR-9.2, D9). Use MerkleMembershipProof for sound but non-anonymous group membership proofs."
)


class AnonymousProofBackend:
    """Deliberately unimplemented placeholder for audited anonymous zk-SNARK proofs (D9)."""

    def generate_proof(self, *args: Any, **kwargs: Any) -> Any:
        """Attempting to generate an anonymous proof raises NotImplementedError (D9)."""
        raise NotImplementedError(AUDIT_PENDING_MESSAGE)

    def verify_proof(self, *args: Any, **kwargs: Any) -> bool:
        """Attempting to verify an anonymous proof raises NotImplementedError (D9)."""
        raise NotImplementedError(AUDIT_PENDING_MESSAGE)
