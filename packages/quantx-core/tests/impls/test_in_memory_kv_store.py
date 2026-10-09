"""
Layer: 0
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_core.types.ttl.TTL
Implements: pytest test functions for InMemoryKVStore
Outside: Testing anything other than InMemoryKVStore unit behavior.
Inside: Round-trip set/get, delete behavior, TTL expiration with fake clock, capacity cap presence.
Security notes: Foundation rules in 10-security-requirements.md; SR-3 specific testing is in test_sr_03.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.types.ttl import TTL


def test_in_memory_kv_store_roundtrip(fake_clock: Any) -> None:
    store = InMemoryKVStore(clock=fake_clock, max_entries=10)
    store.set("test_key", b"test_value")
    assert store.get("test_key") == b"test_value"
    assert store.get("nonexistent") is None


def test_in_memory_kv_store_delete(fake_clock: Any) -> None:
    store = InMemoryKVStore(clock=fake_clock, max_entries=10)
    store.set("key_to_delete", b"some_value")
    assert store.get("key_to_delete") == b"some_value"
    store.delete("key_to_delete")
    assert store.get("key_to_delete") is None
    # Deleting nonexistent key does not raise
    store.delete("key_to_delete")


def test_in_memory_kv_store_ttl_expiration(fake_clock: Any) -> None:
    store = InMemoryKVStore(clock=fake_clock, max_entries=10)
    store.set("temp_key", b"ephemeral", ttl=TTL(seconds=30))
    assert store.get("temp_key") == b"ephemeral"

    # Advance fake clock by 29 seconds: still valid
    fake_clock.advance(29)
    assert store.get("temp_key") == b"ephemeral"

    # Advance 2 more seconds: expired
    fake_clock.advance(2)
    assert store.get("temp_key") is None


def test_in_memory_kv_store_cap_exists(fake_clock: Any) -> None:
    store = InMemoryKVStore(clock=fake_clock, max_entries=2)
    store.set("k1", b"v1")
    store.set("k2", b"v2")
    with pytest.raises(BackendUnavailableError):
        store.set("k3", b"v3")
