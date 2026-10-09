"""
Layer: 0
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore
Implements: The mandatory automated security test for SR-3.
Outside: Anything not directly required to verify SR-3.
Inside: Hard capacity cap enforcement, explicit rejection on overflow, and bounded size verification.
Security notes: SR-3. This file is the enforcement check for SR-3.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.types.ttl import TTL


def test_sr_03_in_memory_max_entries_cap_rejection(fake_clock: Any) -> None:
    cap = 5
    store = InMemoryKVStore(clock=fake_clock, max_entries=cap)

    # Fill to capacity
    for i in range(cap):
        store.set(f"key_{i}", f"val_{i}".encode("utf-8"))

    assert len(store) == cap

    # New entry past cap must be explicitly rejected with BackendUnavailableError
    with pytest.raises(BackendUnavailableError):
        store.set("overflow_key", b"overflow_value")

    # Store must not grow past cap under sustained attempts
    for j in range(10):
        with pytest.raises(BackendUnavailableError):
            store.set(f"overflow_{j}", b"overflow")

    assert len(store) == cap


def test_sr_03_in_memory_updating_existing_key_allowed(fake_clock: Any) -> None:
    cap = 3
    store = InMemoryKVStore(clock=fake_clock, max_entries=cap)

    for i in range(cap):
        store.set(f"k_{i}", f"v_{i}".encode("utf-8"))

    # Updating existing key must succeed without increasing count
    store.set("k_0", b"new_v_0")
    assert store.get("k_0") == b"new_v_0"
    assert len(store) == cap


def test_sr_03_in_memory_expired_entry_frees_slot(fake_clock: Any) -> None:
    cap = 2
    store = InMemoryKVStore(clock=fake_clock, max_entries=cap)

    store.set("temp", b"val", ttl=TTL(seconds=10))
    store.set("perm", b"val")

    assert len(store) == 2
    with pytest.raises(BackendUnavailableError):
        store.set("blocked", b"val")

    # Advance clock past TTL
    fake_clock.advance(15)

    # Now expired key is evicted, freeing slot for new key
    store.set("unblocked", b"val")
    assert store.get("unblocked") == b"val"
    assert len(store) == 2
