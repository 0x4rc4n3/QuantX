"""Unit tests for BackupCodeManager non-adversarial path.

Layer: 6-7
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_core.impls.in_memory_replay_store.InMemoryReplayStore, quantx_wallet.backup_code_manager.BackupCodeManager
Implements: Pytest tests validating genuine backup code verification
Outside: Replay rejection adversarial test suite
Inside: Code registration, hash verification, and single-use consumption
Security notes: Confirms FR-6.4 at unit level: genuine code verifies successfully once.
"""

from __future__ import annotations

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_wallet.backup_code_manager import BackupCodeManager


def test_backup_code_manager_genuine_verification(
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
) -> None:
    manager = BackupCodeManager(replay_store=replay_store, kv_store=kv_store)

    manager.register_codes("alice", ["code-1111-2222", "code-3333-4444"])

    # First attempt succeeds
    assert manager.verify("alice", "code-1111-2222") is True

    # Unknown code fails
    assert manager.verify("alice", "code-9999-9999") is False

    # Second registered code succeeds
    assert manager.verify("alice", "code-3333-4444") is True
