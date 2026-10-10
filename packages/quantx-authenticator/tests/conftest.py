"""Test fixtures for quantx-authenticator test suite.

Layer: 5
Depends on: quantx_authenticator, quantx_core
Implements: pytest fixtures for test-fixture OTP secrets, KeyValueStore, ReplayStore, RateLimiter, and fake Clock
Outside: Individual assertion logic
Inside: Fixture factory construction
Security notes: Test credentials and secrets are ephemeral in-memory fixtures.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.clock import Clock


class FakeClock(Clock):
    """Controllable clock for deterministic time testing."""

    def __init__(self, initial_time: datetime | None = None) -> None:
        self._current_time = initial_time or datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, new_time: datetime) -> None:
        self._current_time = new_time

    def advance(self, seconds: float) -> None:
        from datetime import timedelta

        self._current_time += timedelta(seconds=seconds)


@pytest.fixture
def fake_clock() -> FakeClock:
    """Provide a controllable clock for tests."""
    return FakeClock()


@pytest.fixture
def kv_store(fake_clock: FakeClock) -> InMemoryKVStore:
    """Provide an in-memory key-value store."""
    return InMemoryKVStore(clock=fake_clock, max_entries=1000)


@pytest.fixture
def replay_store(kv_store: InMemoryKVStore) -> InMemoryReplayStore:
    """Provide an in-memory replay store."""
    return InMemoryReplayStore(kv_store=kv_store, prefix="test_replay:")


@pytest.fixture
def rate_limiter(kv_store: InMemoryKVStore, fake_clock: FakeClock) -> InMemoryRateLimiter:
    """Provide an in-memory rate limiter."""
    return InMemoryRateLimiter(kv_store=kv_store, clock=fake_clock, limit=5, window_seconds=60)


@pytest.fixture
def canonicalizer() -> JCSCanonicalizer:
    """Provide a JCS canonicalizer."""
    return JCSCanonicalizer()


@pytest.fixture
def test_secret() -> bytes:
    """RFC 4226 test vector secret: 20 bytes ascii '12345678901234567890'."""
    return b"12345678901234567890"
