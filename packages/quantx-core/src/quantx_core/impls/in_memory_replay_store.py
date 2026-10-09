"""
Layer: 0
Depends on: quantx_core.interfaces.replay_store.ReplayStore, quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.types.ttl.TTL
Implements: InMemoryReplayStore
Outside: Semantic classification of credentials (challenge, token, code, push).
Inside: Atomic consume-once replay protection storing state via KeyValueStore.
Security notes: SR-11 / FR-4.2. State persisted through injected KeyValueStore; atomic consume-once semantics.
"""

from __future__ import annotations

import threading

from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.types.ttl import TTL


class InMemoryReplayStore(ReplayStore):
    """
    Reference ReplayStore implementation backing Recipe A (dev/testing).
    """

    def __init__(self, kv_store: KeyValueStore, prefix: str = "replay:") -> None:
        self._kv_store = kv_store
        self._prefix = prefix
        self._lock = threading.Lock()

    def consume_once(self, token: str, ttl: TTL | None = None) -> bool:
        """
        Atomically checks and records consumption of the given token.

        Returns True on the first successful consumption, False on subsequent attempts.
        """
        key = f"{self._prefix}{token}"
        with self._lock:
            existing = self._kv_store.get(key)
            if existing is not None:
                return False
            self._kv_store.set(key, b"consumed", ttl=ttl)
            return True
