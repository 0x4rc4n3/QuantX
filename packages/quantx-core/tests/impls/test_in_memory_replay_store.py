"""
Layer: 0
Depends on: quantx_core.impls.in_memory_replay_store.InMemoryReplayStore, quantx_core.impls.in_memory_kv_store.InMemoryKVStore
Implements: pytest test functions for InMemoryReplayStore
Outside: Testing anything other than InMemoryReplayStore.
Inside: Single-use consumption verification and replay rejection.
Security notes: Mandatory replay check under SR-11/FR-4.2.
"""

from __future__ import annotations

from typing import Any

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore


def test_in_memory_replay_store_consume_once(fake_clock: Any) -> None:
    kv = InMemoryKVStore(clock=fake_clock, max_entries=100)
    replay = InMemoryReplayStore(kv_store=kv)

    # First call must return True
    assert replay.consume_once("token-12345") is True

    # Immediate second call with same token must return False
    assert replay.consume_once("token-12345") is False

    # Different token must succeed
    assert replay.consume_once("token-67890") is True

    # And replaying the second token must return False
    assert replay.consume_once("token-67890") is False
