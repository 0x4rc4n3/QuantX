"""Vault metadata value type authenticated within AEAD AAD.

Layer: 6
Depends on: quantx_core.interfaces.canonicalizer.Canonicalizer, quantx_core.interfaces.clock.Clock
Implements: VaultMetadata immutable value type and AAD serialization
Outside: Backend persistence and encryption mechanics
Inside: Schema definition, field validation, and canonical AAD generation
Security notes: Vault metadata is included in AEAD AAD so any tampering is detected (SR-9).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.clock import Clock

VALID_ROTATION_STATES: frozenset[str] = frozenset({"active", "retired", "revoked"})

VALID_KEY_FORMATS: frozenset[str] = frozenset(
    {
        "ed25519-raw-v1",
        "ecdsa-p256-pkcs8-v1",
        "x25519-raw-v1",
        "mldsa65-seed-v1",
        "mldsa87-seed-v1",
        "mlkem768-seed-v1",
        "mlkem1024-seed-v1",
    }
)


@dataclass(frozen=True)
class VaultMetadata:
    """Immutable metadata record authenticated inside AEAD AAD."""

    key_id: str
    algorithm: str
    created_at: str
    rotation_state: str = "active"
    key_format: str = "ed25519-raw-v1"

    def __post_init__(self) -> None:
        if not self.key_id:
            raise ValueError("key_id cannot be empty")
        if not self.algorithm:
            raise ValueError("algorithm cannot be empty")
        if self.rotation_state not in VALID_ROTATION_STATES:
            raise ValueError(
                f"Invalid rotation_state '{self.rotation_state}', must be one of {sorted(VALID_ROTATION_STATES)}"
            )
        if self.key_format not in VALID_KEY_FORMATS:
            raise ValueError(
                f"Invalid key_format '{self.key_format}', must be one of {sorted(VALID_KEY_FORMATS)}"
            )

    @classmethod
    def create(
        cls,
        key_id: str,
        algorithm: str,
        clock: Clock,
        rotation_state: str = "active",
        key_format: str = "ed25519-raw-v1",
    ) -> VaultMetadata:
        """Create new metadata stamping creation time from injected Clock."""
        created_at_iso = clock.now().isoformat()
        return cls(
            key_id=key_id,
            algorithm=algorithm,
            created_at=created_at_iso,
            rotation_state=rotation_state,
            key_format=key_format,
        )

    def to_dict(self) -> dict[str, str]:
        """Convert metadata to dictionary representation."""
        return {
            "algorithm": self.algorithm,
            "created_at": self.created_at,
            "key_format": self.key_format,
            "key_id": self.key_id,
            "rotation_state": self.rotation_state,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> VaultMetadata:
        """Parse metadata from dictionary representation."""
        return cls(
            key_id=str(data["key_id"]),
            algorithm=str(data["algorithm"]),
            created_at=str(data["created_at"]),
            rotation_state=str(data.get("rotation_state", "active")),
            key_format=str(data.get("key_format", "ed25519-raw-v1")),
        )

    def to_aad_bytes(self, canonicalizer: Canonicalizer) -> bytes:
        """Produce canonical JCS AAD bytes for AEAD authentication (SR-8, SR-9)."""
        return canonicalizer.canonicalize(self.to_dict())
