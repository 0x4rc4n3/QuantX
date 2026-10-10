"""Backup code recovery manager with single-use consume-once semantics.

Layer: 6-7
Depends on: quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.interfaces.replay_store.ReplayStore
Implements: BackupCodeManager
Outside: Generating and delivering backup codes out-of-band to users
Inside: SHA-256 hash comparison and single-use consumption in ReplayStore
Security notes: FR-6.4/SR-11: exactly-once verification via ReplayStore; never stores plaintext codes.
"""

from __future__ import annotations

import hashlib

from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.replay_store import ReplayStore


class BackupCodeManager:
    """Manages verification and single-use consumption of recovery backup codes."""

    def __init__(
        self,
        replay_store: ReplayStore,
        kv_store: KeyValueStore,
    ) -> None:
        self._replay_store = replay_store
        self._kv_store = kv_store

    def _hash_code(self, code: str) -> str:
        return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()

    def register_code(self, subject_id: str, code: str) -> None:
        """Register a valid hashed backup code for a subject."""
        if not subject_id or not code:
            raise ValueError("subject_id and code cannot be empty")
        code_hash = self._hash_code(code)
        storage_key = f"backup_code:{subject_id}:{code_hash}"
        self._kv_store.set(storage_key, b"1")

    def register_codes(self, subject_id: str, codes: list[str]) -> None:
        """Register multiple backup codes for a subject."""
        for code in codes:
            self.register_code(subject_id, code)

    def verify(self, subject_id: str, code: str) -> bool:
        """Verify and consume a backup code exactly once (FR-6.4, SR-11)."""
        if not subject_id or not code:
            return False

        code_hash = self._hash_code(code)
        replay_key = f"backup_code_consumed:{subject_id}:{code_hash}"
        storage_key = f"backup_code:{subject_id}:{code_hash}"

        # If code hash was never registered or already deleted, fail
        stored = self._kv_store.get(storage_key)
        if stored is None:
            return False

        # Consume once atomically in ReplayStore; fail if already consumed
        if not self._replay_store.consume_once(replay_key):
            return False

        self._kv_store.delete(storage_key)
        return True
