"""
Layer: 0
Depends on: quantx_core.interfaces.rate_limiter.RateLimiter, quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.interfaces.clock.Clock, quantx_core.types.ttl.TTL
Implements: InMemoryRateLimiter
Outside: Choosing which identity keys to gate on and wiring independent instances.
Inside: Fixed-window check-and-count rate limiting storing state via KeyValueStore.
Security notes: FR-4.4 / FR-5.2 / SR-5. State persisted through injected KeyValueStore; fixed window boundary semantics (D-015).
"""

from __future__ import annotations

import threading

from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.rate_limiter import RateLimiter
from quantx_core.types.ttl import TTL


class InMemoryRateLimiter(RateLimiter):
    """
    Reference RateLimiter implementation backing Recipe A (dev/testing).
    Enforces a fixed-window counter using the injected KeyValueStore and Clock (D-015).
    """

    def __init__(
        self,
        kv_store: KeyValueStore,
        clock: Clock,
        limit: int,
        window_seconds: int = 60,
        prefix: str = "rate_limit:",
    ) -> None:
        if limit <= 0:
            raise ValueError("Rate limit must be greater than zero")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")
        self._kv_store = kv_store
        self._clock = clock
        self._limit = limit
        self._window_seconds = window_seconds
        self._prefix = prefix
        self._lock = threading.Lock()

    def allow(self, identity_key: str) -> bool:
        """
        Evaluates whether an attempt by identity_key is permitted within the current window.

        Window boundary behavior: The window resets every window_seconds at unix timestamp
        boundaries (current_timestamp // window_seconds). Attempts within the window are counted.
        When count >= limit, subsequent calls in that window return False.
        """
        now = self._clock.now()
        current_ts = int(now.timestamp())
        window_index = current_ts // self._window_seconds
        store_key = f"{self._prefix}{identity_key}:{window_index}"

        with self._lock:
            raw_val = self._kv_store.get(store_key)
            current_count = int(raw_val.decode("utf-8")) if raw_val is not None else 0

            if current_count >= self._limit:
                return False

            new_count = current_count + 1
            # Maintain TTL slightly longer than window to ensure window completes cleanly
            ttl = TTL(seconds=self._window_seconds * 2)
            self._kv_store.set(store_key, str(new_count).encode("utf-8"), ttl=ttl)
            return True
