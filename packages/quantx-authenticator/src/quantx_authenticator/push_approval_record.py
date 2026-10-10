"""Push approval record value type.

Layer: 5
Depends on: quantx_core.types.ttl.TTL, quantx_core.interfaces.canonicalizer.Canonicalizer
Implements: PushApprovalRecord immutable value type with canonical serialization
Outside: Lifecycle transitions and network notifications
Inside: Approval identifier, subject binding, timestamps, and JSON serialization
Security notes: Immutable value type; single-use consumption is enforced by ReplayStore per SR-11.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from quantx_core.interfaces.canonicalizer import Canonicalizer


@dataclass(frozen=True)
class PushApprovalRecord:
    """Immutable representation of a push notification approval request."""

    approval_id: str
    subject_id: str
    issued_at: datetime
    expires_at: datetime
    consumed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert record fields to a dictionary for canonicalization."""
        return {
            "approval_id": self.approval_id,
            "subject_id": self.subject_id,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "consumed": self.consumed,
        }

    def to_bytes(self, canonicalizer: Canonicalizer) -> bytes:
        """Serialize record canonically through Layer 0 Canonicalizer."""
        return canonicalizer.canonicalize(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> PushApprovalRecord:
        """Deserialize record from JSON string."""
        data = json.loads(json_str)
        issued_at = datetime.fromisoformat(data["issued_at"])
        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=timezone.utc)
        expires_at = datetime.fromisoformat(data["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return cls(
            approval_id=str(data["approval_id"]),
            subject_id=str(data["subject_id"]),
            issued_at=issued_at,
            expires_at=expires_at,
            consumed=bool(data.get("consumed", False)),
        )
