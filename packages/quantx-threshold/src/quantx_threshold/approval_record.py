"""Approval record value type submitted toward threshold quorum.

Layer: 8
Depends on: quantx_core.types.algorithm_id.AlgorithmId
Implements: ApprovalRecord
Outside: Quorum evaluation and state persistence
Inside: Immutable approval value holding policy reference, key identifier, signature, and message
Security notes: Immutable once submitted; each approval verified via SignatureCombiner.
"""

from __future__ import annotations

from dataclasses import dataclass

from quantx_core.types.algorithm_id import AlgorithmId


@dataclass(frozen=True)
class ApprovalRecord:
    """Immutable record of one signature submitted toward a threshold policy quorum."""

    policy_id: str
    key_id: str
    algorithm: AlgorithmId
    signature: bytes
    message: bytes

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id cannot be empty")
        if not self.key_id:
            raise ValueError("key_id cannot be empty")
        if not self.signature:
            raise ValueError("signature cannot be empty")
