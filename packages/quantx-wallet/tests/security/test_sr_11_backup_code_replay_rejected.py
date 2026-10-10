"""Mandatory security test SR-11: Consumed backup code cannot be replayed.

Layer: 6-7
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_core.impls.in_memory_replay_store.InMemoryReplayStore, quantx_wallet.backup_code_manager.BackupCodeManager
Implements: SR-11 mandatory test verifying single-use consume-once semantics for backup codes
Outside: Push approval replay protection (tested in quantx-authenticator)
Inside: First verification succeeds, subsequent replay attempts are rejected
Security notes: SR-11: Backup codes are consumed through ReplayStore; replay is rejected.
"""

from __future__ import annotations

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_wallet.backup_code_manager import BackupCodeManager


def test_sr_11_backup_code_replay_rejected(
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
) -> None:
    manager = BackupCodeManager(replay_store=replay_store, kv_store=kv_store)

    manager.register_code("subject-123", "backup-code-secret-value-123")

    # First attempt: succeeds
    first_result = manager.verify("subject-123", "backup-code-secret-value-123")
    assert first_result is True

    # Second attempt (replay): fails
    second_result = manager.verify("subject-123", "backup-code-secret-value-123")
    assert second_result is False

    # Third attempt (replay): fails
    third_result = manager.verify("subject-123", "backup-code-secret-value-123")
    assert third_result is False
