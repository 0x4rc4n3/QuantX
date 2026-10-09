"""
Layer: 0
Depends on: quantx_core.impls.in_memory_rate_limiter.InMemoryRateLimiter, quantx_core.impls.in_memory_kv_store.InMemoryKVStore
Implements: pytest test functions for InMemoryRateLimiter
Outside: Testing anything other than InMemoryRateLimiter.
Inside: Rate limit check under/over thresholds, window boundary transitions, and instance independence.
Security notes: Non-security unit test for FR-4.4/SR-5 limiter behaviors.
"""

from __future__ import annotations

from typing import Any

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter


def test_in_memory_rate_limiter_under_and_over_limit(fake_clock: Any) -> None:
    kv = InMemoryKVStore(clock=fake_clock, max_entries=100)
    limiter = InMemoryRateLimiter(kv_store=kv, clock=fake_clock, limit=3, window_seconds=60)

    # First 3 attempts should be allowed
    assert limiter.allow("user-1") is True
    assert limiter.allow("user-1") is True
    assert limiter.allow("user-1") is True

    # 4th attempt trips limit
    assert limiter.allow("user-1") is False

    # Window rollover
    fake_clock.advance(61)
    assert limiter.allow("user-1") is True


def test_in_memory_rate_limiter_instance_isolation(fake_clock: Any) -> None:
    kv = InMemoryKVStore(clock=fake_clock, max_entries=100)
    user_limiter = InMemoryRateLimiter(
        kv_store=kv, clock=fake_clock, limit=2, window_seconds=60, prefix="user_limit:"
    )
    global_limiter = InMemoryRateLimiter(
        kv_store=kv, clock=fake_clock, limit=5, window_seconds=60, prefix="global_limit:"
    )

    # Trip user limiter
    assert user_limiter.allow("user-1") is True
    assert user_limiter.allow("user-1") is True
    assert user_limiter.allow("user-1") is False

    # Global limiter is separate and still allows
    assert global_limiter.allow("global") is True
    assert global_limiter.allow("global") is True
