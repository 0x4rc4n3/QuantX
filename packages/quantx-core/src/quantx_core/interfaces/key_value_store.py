"""
Layer: 0
Depends on: quantx_core.types.ttl.TTL
Implements: KeyValueStore
Outside: Replay and rate-limiting semantics (handled via ReplayStore and RateLimiter).
Inside: The get, set, and delete method signatures for state persistence.
Security notes: FR-0.2. The single approved path for stateful persistence; no component may hold ad hoc caches.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from quantx_core.types.ttl import TTL


@runtime_checkable
class KeyValueStore(Protocol):
    """
    Foundational interface for state storage across QuantX.
    """

    def get(self, key: str) -> bytes | None:
        """
        Retrieves value bytes by key, or None if expired or not found.
        """
        ...

    def set(self, key: str, value: bytes, ttl: TTL | None = None) -> None:
        """
        Stores value bytes under key with an optional TTL duration.
        """
        ...

    def delete(self, key: str) -> None:
        """
        Deletes key and its stored value.
        """
        ...
