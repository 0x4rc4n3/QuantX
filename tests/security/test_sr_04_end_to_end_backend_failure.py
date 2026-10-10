"""End-to-end security test for SR-4: Networked backend failure fails closed.

Layer: cross-cutting
Depends on: quantx_core.interfaces.key_value_store.KeyValueStore, quantx_session.session_orchestrator.SessionOrchestrator, quantx_core.exceptions.BackendUnavailableError
Implements: Mandatory full-stack end-to-end test for SR-4 (backend failure fails closed)
Outside: Every other numbered SR item
Inside: Simulate backend store outage mid-flow and confirm system fails closed without inconsistent partial state
Wire format: Native storage structures
Security notes: Mandatory SR-4 end-to-end confirmation across quantx-core and quantx-session
"""

from __future__ import annotations

import pytest
from quantx_core.exceptions import BackendUnavailableError
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.system_clock import SystemClock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.types.ttl import TTL
from quantx_session.session_orchestrator import SessionOrchestrator


class FailingKVStore(KeyValueStore):
    """Simulates a networked KeyValueStore backend outage (e.g. Redis disconnect)."""

    def get(self, key: str) -> bytes | None:
        raise BackendUnavailableError("Network connection to Redis backend lost (E_BACKEND_DOWN)")

    def set(self, key: str, value: bytes, ttl: TTL | None = None) -> None:
        raise BackendUnavailableError("Network connection to Redis backend lost (E_BACKEND_DOWN)")

    def delete(self, key: str) -> bool:
        raise BackendUnavailableError("Network connection to Redis backend lost (E_BACKEND_DOWN)")


def test_sr_04_end_to_end_backend_failure_fails_closed() -> None:
    clock = SystemClock()
    failing_store = FailingKVStore()
    replay_store = InMemoryReplayStore(kv_store=failing_store)
    rate_limiter = InMemoryRateLimiter(
        kv_store=failing_store, clock=clock, limit=10, window_seconds=60
    )

    orchestrator = SessionOrchestrator(
        kv_store=failing_store,
        replay_store=replay_store,
        identity_rate_limiter=rate_limiter,
        global_rate_limiter=rate_limiter,
        clock=clock,
        combiners_by_role={},
    )

    # When store fails, finish() must raise BackendUnavailableError, failing closed
    with pytest.raises(BackendUnavailableError, match="E_BACKEND_DOWN"):
        orchestrator.finish(
            challenge_id="chal-dummy-123",
            signed_response=b"dummy_signature",
        )
