"""
Layer: 4
Depends on: TTL (Layer 0)
Implements: SessionToken
Outside: Storage mechanics (KeyValueStore); token validation orchestration (SessionOrchestrator).
Inside: Value type representing a minted session token.
Security notes: Minted only as the last statement after all gates pass (SR-10). Immutable once created.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from quantx_core.interfaces.canonicalizer import Canonicalizer


@dataclass(frozen=True)
class SessionToken:
    """
    Immutable value type representing an authenticated session token.
    """

    token_id: str
    subject_id: str
    issued_at: datetime
    expires_at: datetime
    factors_completed: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.token_id:
            raise ValueError("token_id must be non-empty")
        if not self.subject_id:
            raise ValueError("subject_id must be non-empty")
        if self.issued_at.tzinfo is None:
            raise ValueError("issued_at must be timezone-aware (UTC)")
        if self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware (UTC)")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be strictly after issued_at")
        if not self.factors_completed:
            raise ValueError("factors_completed must contain at least one factor")

    def to_bytes(self, canonicalizer: Canonicalizer | None = None) -> bytes:
        """Serialize to canonical bytes for KeyValueStore storage (RFC 8785, SR-8)."""
        data = {
            "expires_at": self.expires_at.isoformat(),
            "factors_completed": list(self.factors_completed),
            "issued_at": self.issued_at.isoformat(),
            "subject_id": self.subject_id,
            "token_id": self.token_id,
        }
        if canonicalizer is not None:
            return canonicalizer.canonicalize(data)
        from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer

        return JCSCanonicalizer().canonicalize(data)

    @classmethod
    def from_json(cls, raw_json: str) -> SessionToken:
        """Deserialize from JSON string."""
        data: dict[str, Any] = json.loads(raw_json)
        return cls(
            token_id=data["token_id"],
            subject_id=data["subject_id"],
            issued_at=datetime.fromisoformat(data["issued_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            factors_completed=tuple(data["factors_completed"]),
        )
