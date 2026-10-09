"""
Layer: 0
Depends on: quantx_core.impls.redis_kv_store.RedisKVStore
Implements: The mandatory automated security test for SR-4.
Outside: Anything not directly required to verify SR-4.
Inside: Confirms RedisKVStore raises BackendUnavailableError on connection failure (fail-closed).
Security notes: SR-4. This file is the enforcement check for SR-4.
"""

from __future__ import annotations

import pytest
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.impls.redis_kv_store import RedisKVStore
from quantx_core.types.ttl import TTL


class FailingRedisClient:
    """Simulates broken network or disconnected Redis server."""

    def get(self, key: str) -> None:
        raise ConnectionError("Network connection reset by peer")

    def set(self, key: str, value: bytes, ex: int | None = None) -> None:
        raise TimeoutError("Redis cluster timed out")

    def delete(self, key: str) -> None:
        raise ConnectionRefusedError("Connection refused by Redis")


def test_sr_04_redis_backend_failure_get_raises_backend_unavailable() -> None:
    store = RedisKVStore(client=FailingRedisClient())
    with pytest.raises(BackendUnavailableError) as exc_info:
        store.get("key")
    assert "Redis backend failure" in str(exc_info.value)


def test_sr_04_redis_backend_failure_set_raises_backend_unavailable() -> None:
    store = RedisKVStore(client=FailingRedisClient())
    with pytest.raises(BackendUnavailableError) as exc_info:
        store.set("key", b"value", ttl=TTL(seconds=60))
    assert "Redis backend failure" in str(exc_info.value)


def test_sr_04_redis_backend_failure_delete_raises_backend_unavailable() -> None:
    store = RedisKVStore(client=FailingRedisClient())
    with pytest.raises(BackendUnavailableError) as exc_info:
        store.delete("key")
    assert "Redis backend failure" in str(exc_info.value)
