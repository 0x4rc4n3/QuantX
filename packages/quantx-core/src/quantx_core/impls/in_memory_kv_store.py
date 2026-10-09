"""
Layer: 0
Depends on: quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.interfaces.clock.Clock, quantx_core.types.ttl.TTL
Implements: InMemoryKVStore
Outside: Anything not directly part of the KeyValueStore contract.
Inside: Thread-safe in-memory key-value store with explicit TTL expiration and hard capacity cap.
Security notes: SR-3. In-memory store has a hard max_entries cap; never grows unbounded.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Dict, Optional, Tuple

from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.types.ttl import TTL


class InMemoryKVStore(KeyValueStore):
    """
    Reference in-memory KeyValueStore implementation backing Recipe A (dev/testing).
    """

    def __init__(self, clock: Clock, max_entries: int = 1000) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be a positive integer")
        self._clock = clock
        self._max_entries = max_entries
        self._store: Dict[str, Tuple[bytes, Optional[datetime]]] = {}
        self._lock = threading.Lock()

    def _evict_expired_locked(self, current_time: datetime) -> None:
        expired_keys = [
            k
            for k, (_, expires_at) in self._store.items()
            if expires_at is not None and current_time >= expires_at
        ]
        for k in expired_keys:
            del self._store[k]

    def get(self, key: str) -> bytes | None:
        with self._lock:
            if key not in self._store:
                return None
            value, expires_at = self._store[key]
            if expires_at is not None and self._clock.now() >= expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: bytes, ttl: TTL | None = None) -> None:
        now = self._clock.now()
        with self._lock:
            self._evict_expired_locked(now)

            if key not in self._store and len(self._store) >= self._max_entries:
                raise BackendUnavailableError(
                    f"InMemoryKVStore hard limit reached: max_entries={self._max_entries} (SR-3)"
                )

            expires_at = now + ttl.to_timedelta() if ttl is not None else None
            self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def __len__(self) -> int:
        with self._lock:
            self._evict_expired_locked(self._clock.now())
            return len(self._store)
