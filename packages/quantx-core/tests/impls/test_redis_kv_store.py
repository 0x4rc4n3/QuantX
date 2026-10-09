"""
Layer: 0
Depends on: quantx_core.impls.redis_kv_store.RedisKVStore, quantx_core.types.ttl.TTL
Implements: pytest test functions for RedisKVStore
Outside: Testing anything other than RedisKVStore unit behavior.
Inside: Round-trip set/get, delete, and TTL pass-through to Redis client.
Security notes: Non-security test; failure handling test is in test_sr_04.
"""

from __future__ import annotations

from typing import Dict, Optional

from quantx_core.impls.redis_kv_store import RedisKVStore
from quantx_core.types.ttl import TTL


class MockRedisClient:
    """In-memory mock of redis.Redis client."""

    def __init__(self) -> None:
        self.data: Dict[str, bytes] = {}
        self.expirations: Dict[str, Optional[int]] = {}

    def get(self, key: str) -> bytes | None:
        return self.data.get(key)

    def set(self, key: str, value: bytes, ex: Optional[int] = None) -> None:
        self.data[key] = bytes(value)
        self.expirations[key] = ex

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.expirations.pop(key, None)


def test_redis_kv_store_roundtrip() -> None:
    client = MockRedisClient()
    store = RedisKVStore(client=client)

    store.set("test_key", b"test_value")
    assert store.get("test_key") == b"test_value"
    assert store.get("missing_key") is None


def test_redis_kv_store_ttl_passthrough() -> None:
    client = MockRedisClient()
    store = RedisKVStore(client=client)

    store.set("session_key", b"active_session", ttl=TTL(seconds=300))
    assert client.data["session_key"] == b"active_session"
    assert client.expirations["session_key"] == 300


def test_redis_kv_store_delete() -> None:
    client = MockRedisClient()
    store = RedisKVStore(client=client)

    store.set("key_1", b"val_1")
    assert store.get("key_1") == b"val_1"
    store.delete("key_1")
    assert store.get("key_1") is None
