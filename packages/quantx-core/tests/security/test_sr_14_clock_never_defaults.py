"""
Layer: 0
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_core.impls.in_memory_rate_limiter.InMemoryRateLimiter
Implements: The mandatory automated security test for SR-14.
Outside: Anything not directly required to verify SR-14.
Inside: Verifies timestamp-consuming implementations rely strictly on injected Clock.
Security notes: SR-14. Timestamps come only from an injected Clock, never defaulted against wall-clock.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.types.ttl import TTL


def test_sr_14_kv_store_uses_injected_clock_strictly(fake_clock: Any) -> None:
    # Set fake clock to year 2099
    future_time = datetime(2099, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    fake_clock.set_time(future_time)

    store = InMemoryKVStore(clock=fake_clock, max_entries=10)
    store.set("key", b"value", ttl=TTL(seconds=60))

    # Real wall-clock time is far in the past compared to 2099.
    # If the store defaulted to datetime.now(), the entry would appear immediately expired or wrong.
    assert store.get("key") == b"value"

    # Advance fake clock by 61 seconds (in 2099)
    fake_clock.advance(61)
    # Entry expires according to fake clock
    assert store.get("key") is None


def test_sr_14_rate_limiter_uses_injected_clock_strictly(fake_clock: Any) -> None:
    # Set fake clock to year 2040
    start_time = datetime(2040, 5, 10, 10, 0, 0, tzinfo=timezone.utc)
    fake_clock.set_time(start_time)

    store = InMemoryKVStore(clock=fake_clock, max_entries=100)
    limiter = InMemoryRateLimiter(kv_store=store, clock=fake_clock, limit=1, window_seconds=30)

    assert limiter.allow("user-a") is True
    assert limiter.allow("user-a") is False

    # Advance fake clock past window
    fake_clock.advance(31)
    # Limiter resets based strictly on fake clock
    assert limiter.allow("user-a") is True
