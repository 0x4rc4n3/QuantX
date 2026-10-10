"""Unit tests for DeviceLinker.

Layer: 6-7
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_core.impls.in_memory_replay_store.InMemoryReplayStore, quantx_wallet.device_linker.DeviceLinker
Implements: Pytest tests validating device pairing token lifecycle
Outside: Cross-device transport mechanisms
Inside: Token issuance, 256-bit entropy, single-use consumption, and replay rejection
Security notes: Confirms Layer-7 done criterion: pairing tokens cannot be replayed.
"""

from __future__ import annotations

from typing import Any

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_wallet.device_linker import DeviceLinker


def test_device_linker_token_issuance_and_consumption(
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
) -> None:
    linker = DeviceLinker(
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
        token_ttl_seconds=600,
    )

    token = linker.issue_pairing_token("bob")
    assert isinstance(token, str)
    assert len(token) == 64  # 32 bytes hex = 64 hex chars = 256 bits

    # First consumption succeeds
    assert linker.consume_pairing_token(token) is True

    # Immediate second consumption fails (replay protection)
    assert linker.consume_pairing_token(token) is False


def test_device_linker_invalid_or_unknown_token_fails(
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
) -> None:
    linker = DeviceLinker(
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
    )

    assert linker.consume_pairing_token("unknown-token") is False
    assert linker.consume_pairing_token("") is False
