"""Device linking manager for pairing tokens with replay prevention and TTL expiry.

Layer: 6-7
Depends on: quantx_core.interfaces.clock.Clock, quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.interfaces.replay_store.ReplayStore, quantx_core.types.ttl.TTL
Implements: DeviceLinker
Outside: Out-of-band device-to-device transport mechanisms
Inside: 256-bit pairing token issuance, TTL expiry, and single-use consumption
Security notes: Consume-once via ReplayStore prevents pairing token replay; 10-minute TTL enforces freshness (D-015).
"""

from __future__ import annotations

import secrets

from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.types.ttl import TTL


class DeviceLinker:
    """Manages issuance and single-use consumption of device pairing tokens."""

    def __init__(
        self,
        replay_store: ReplayStore,
        kv_store: KeyValueStore,
        clock: Clock,
        token_ttl_seconds: int = 600,
        canonicalizer: Canonicalizer | None = None,
    ) -> None:
        self._replay_store = replay_store
        self._kv_store = kv_store
        self._clock = clock
        self._token_ttl = TTL(seconds=token_ttl_seconds)
        self._canonicalizer: Canonicalizer = canonicalizer or JCSCanonicalizer()

    def issue_pairing_token(self, subject_id: str) -> str:
        """Issue a cryptographically secure 256-bit device-pairing token (D-015)."""
        if not subject_id:
            raise ValueError("subject_id cannot be empty")

        token = secrets.token_hex(32)  # 256 bits of entropy
        payload = {
            "issued_at": self._clock.now().isoformat(),
            "subject_id": subject_id,
            "token": token,
        }
        storage_key = f"device_link:{token}"
        self._kv_store.set(
            storage_key,
            self._canonicalizer.canonicalize(payload),
            ttl=self._token_ttl,
        )
        return token

    def consume_pairing_token(self, token: str) -> bool:
        """Consume a device pairing token exactly once; fails if replayed or expired."""
        if not token:
            return False

        storage_key = f"device_link:{token}"
        replay_key = f"device_link_consumed:{token}"

        stored = self._kv_store.get(storage_key)
        if stored is None:
            return False

        if not self._replay_store.consume_once(replay_key, ttl=self._token_ttl):
            return False

        self._kv_store.delete(storage_key)
        return True
