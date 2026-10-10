"""Shared test fixtures for end-to-end security register suite across Layers 0-10.

Layer: cross-cutting
Depends on: quantx_core, quantx_crypto_adapters, quantx_combiners, quantx_registry, quantx_session, quantx_authenticator, quantx_wallet, quantx_threshold, quantx_zkp, quantx_compliance
Implements: Pytest fixtures for full-stack end-to-end security register tests
Outside: Assertions themselves
Inside: Full-stack fixture construction for Recipe A and wired components across Layers 0-10
Wire format: In-memory test fixture objects
Security notes: Foundation for end-to-end SR-1 through SR-15 verification across packages
"""

from __future__ import annotations

import datetime
from datetime import timezone

import pytest
from quantx_core.interfaces.clock import Clock
from quantx_session.default_setup import default_setup


class ControllableClock(Clock):
    """Controllable test clock for time manipulation in end-to-end tests."""

    def __init__(self, start_time: datetime.datetime | None = None) -> None:
        self._current_time = start_time or datetime.datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        )

    def now(self) -> datetime.datetime:
        return self._current_time

    def advance(self, seconds: float) -> None:
        self._current_time += datetime.timedelta(seconds=seconds)


@pytest.fixture
def controllable_clock() -> ControllableClock:
    return ControllableClock()


@pytest.fixture
def recipe_a_stack(controllable_clock: ControllableClock):
    """Recipe A full in-memory stack fixture with controllable clock."""
    issuer, orchestrator, registry = default_setup(custom_clock=controllable_clock)
    return {
        "issuer": issuer,
        "orchestrator": orchestrator,
        "registry": registry,
        "clock": controllable_clock,
    }
