"""
Layer: 4
Depends on: Mode, TTL (Layer 0)
Implements: ChallengeRecord
Outside: Storage mechanics (KeyValueStore); verification logic (SessionOrchestrator).
Inside: Value type representing an issued challenge.
Security notes: Immutable value type; required_mode is fixed server-side at issuance and cannot be overridden.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.types.mode import Mode


@dataclass(frozen=True)
class ChallengeRecord:
    """
    Immutable value type representing a stored authentication challenge.
    """

    challenge_id: str
    subject_id: str
    role_id: str
    nonce: bytes
    issued_at: datetime
    expires_at: datetime
    required_mode: Mode

    def __post_init__(self) -> None:
        if not self.challenge_id:
            raise ValueError("challenge_id must be non-empty")
        if not self.subject_id:
            raise ValueError("subject_id must be non-empty")
        if not self.role_id:
            raise ValueError("role_id must be non-empty")
        if not self.nonce:
            raise ValueError("nonce must be non-empty")
        if self.issued_at.tzinfo is None:
            raise ValueError("issued_at must be timezone-aware (UTC)")
        if self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware (UTC)")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be strictly after issued_at")

    def to_bytes(self, canonicalizer: Canonicalizer | None = None) -> bytes:
        """Serialize to canonical bytes for KeyValueStore storage (RFC 8785, SR-8)."""
        data = {
            "challenge_id": self.challenge_id,
            "expires_at": self.expires_at.isoformat(),
            "issued_at": self.issued_at.isoformat(),
            "nonce_hex": self.nonce.hex(),
            "required_mode": self.required_mode.value,
            "role_id": self.role_id,
            "subject_id": self.subject_id,
        }
        if canonicalizer is not None:
            return canonicalizer.canonicalize(data)
        from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer

        return JCSCanonicalizer().canonicalize(data)

    @classmethod
    def from_json(cls, raw_json: str) -> ChallengeRecord:
        """Deserialize from JSON string."""
        data: dict[str, Any] = json.loads(raw_json)
        return cls(
            challenge_id=data["challenge_id"],
            subject_id=data["subject_id"],
            role_id=data["role_id"],
            nonce=bytes.fromhex(data["nonce_hex"]),
            issued_at=datetime.fromisoformat(data["issued_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            required_mode=Mode(data["required_mode"]),
        )
