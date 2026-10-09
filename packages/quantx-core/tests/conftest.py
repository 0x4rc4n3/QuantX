"""
Layer: 0
Depends on: quantx_core.interfaces.clock.Clock, quantx_core.impls.in_memory_kv_store.InMemoryKVStore
Implements: pytest fixtures for quantx-core tests
Outside: Test logic and assertions.
Inside: Fixture construction and teardown.
Security notes: A fake Clock fixture ensures deterministic testing for SR-14 and TTL expiry.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.interfaces.clock import Clock


class FakeClock(Clock):
    """
    Controllable test double for Clock.
    """

    def __init__(self, start_time: datetime | None = None) -> None:
        self._current_time = (
            start_time
            if start_time is not None
            else datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )

    def now(self) -> datetime:
        return self._current_time

    def advance(self, seconds: float) -> None:
        self._current_time += timedelta(seconds=seconds)

    def set_time(self, dt: datetime) -> None:
        self._current_time = dt


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def in_memory_kv_store(fake_clock: FakeClock) -> InMemoryKVStore:
    return InMemoryKVStore(clock=fake_clock, max_entries=100)
