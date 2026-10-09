"""
Layer: 0
Depends on: None
Implements: TTL
Outside: Expiry math (issued_at + ttl -> expires_at) is performed by callers using an injected Clock (SR-14).
Inside: Immutable value type wrapping duration in seconds.
Security notes: Clock injection is required; TTL never reads wall-clock time internally (SR-14).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class TTL:
    """
    Immutable value type wrapping duration for KeyValueStore operations.
    """

    seconds: int

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise ValueError("TTL duration seconds cannot be negative")

    @classmethod
    def from_seconds(cls, seconds: int) -> TTL:
        return cls(seconds=int(seconds))

    @classmethod
    def from_timedelta(cls, td: timedelta) -> TTL:
        return cls(seconds=int(td.total_seconds()))

    def to_timedelta(self) -> timedelta:
        return timedelta(seconds=self.seconds)
