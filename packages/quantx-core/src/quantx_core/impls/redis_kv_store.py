"""
Layer: 0
Depends on: quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_core.types.ttl.TTL
Implements: RedisKVStore
Outside: Anything not directly part of the KeyValueStore contract.
Inside: Networked KeyValueStore implementation backed by Redis with fail-closed connection handling.
Security notes: SR-4. Networked backend failure has a stated, implemented fail-closed decision; raises BackendUnavailableError.
"""

from __future__ import annotations

from typing import Any

from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.types.ttl import TTL

try:
    import redis
except ImportError:
    redis = None  # Optional extra


class RedisKVStore(KeyValueStore):
    """
    Networked KeyValueStore implementation backing Recipe B (enterprise/production).
    Implements a strict fail-closed policy upon connection failure (SR-4).
    """

    def __init__(self, client: Any = None, url: str | None = None) -> None:
        if client is not None:
            self._client = client
        else:
            if redis is None:
                raise BackendUnavailableError(
                    "Redis dependency is not installed. Install with 'quantx-core[redis]'."
                )
            if url is None:
                raise ValueError("Must provide either a Redis client or url")
            try:
                self._client = redis.Redis.from_url(url)
            except Exception as exc:
                raise BackendUnavailableError(f"Failed to initialize Redis client: {exc}") from exc

    def get(self, key: str) -> bytes | None:
        try:
            val = self._client.get(key)
            if val is None:
                return None
            if isinstance(val, str):
                return val.encode("utf-8")
            return bytes(val)
        except Exception as exc:
            raise BackendUnavailableError(
                f"Redis backend failure during get({key}): {exc}"
            ) from exc

    def set(self, key: str, value: bytes, ttl: TTL | None = None) -> None:
        try:
            ex_sec = ttl.seconds if ttl is not None else None
            self._client.set(key, value, ex=ex_sec)
        except Exception as exc:
            raise BackendUnavailableError(
                f"Redis backend failure during set({key}): {exc}"
            ) from exc

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except Exception as exc:
            raise BackendUnavailableError(
                f"Redis backend failure during delete({key}): {exc}"
            ) from exc
