"""Shared test fixtures for quantx-threshold test suite.

Layer: 8
Depends on: quantx_core, quantx_threshold
Implements: Pytest fixtures for threshold policies, replay stores, and verifiers
Outside: Test assertion logic
Inside: Fixture provisioning for unit and security suites
Security notes: Fixtures for testing duplicate key rejection (SR-12) and quorum finalization (FR-8.2).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.interfaces.clock import Clock
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_threshold.threshold_policy import ThresholdPolicy


class FakeClock(Clock):
    """Controllable clock for threshold test fixtures."""

    def __init__(self) -> None:
        self._current_time = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._current_time


class MockVerifier:
    """Mock verifier returning True for valid signatures."""

    def verify(self, signature: bytes, message: bytes) -> bool:
        return signature == b"valid-signature"


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def kv_store(fake_clock: FakeClock) -> InMemoryKVStore:
    return InMemoryKVStore(clock=fake_clock)


@pytest.fixture
def replay_store(kv_store: InMemoryKVStore) -> InMemoryReplayStore:
    return InMemoryReplayStore(kv_store=kv_store)


@pytest.fixture
def sample_keys() -> list[tuple[AlgorithmId, bytes]]:
    return [
        (AlgorithmId.ED25519, b"\x01" * 32),
        (AlgorithmId.ED25519, b"\x02" * 32),
        (AlgorithmId.ED25519, b"\x03" * 32),
    ]


@pytest.fixture
def valid_policy(sample_keys: list[tuple[AlgorithmId, bytes]]) -> ThresholdPolicy:
    return ThresholdPolicy(policy_id="board-approval-policy", keys=sample_keys, m=2)


@pytest.fixture
def mock_verifier() -> MockVerifier:
    return MockVerifier()
