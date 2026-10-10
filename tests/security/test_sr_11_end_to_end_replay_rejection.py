"""End-to-end security test for SR-11: Replay rejection across shared ReplayStore.

Layer: cross-cutting
Depends on: quantx_authenticator.push_authenticator.PushAuthenticator, quantx_wallet.backup_code_manager.BackupCodeManager, quantx_wallet.device_linker.DeviceLinker, quantx_core.impls.in_memory_replay_store.InMemoryReplayStore
Implements: Mandatory full-stack end-to-end test for SR-11 (replay rejected across credentials)
Outside: Every other numbered SR item
Inside: Exercise all credential types against a single shared ReplayStore and confirm replay rejection on reuse
Wire format: Tokens and approval structures
Security notes: Mandatory SR-11 end-to-end confirmation across quantx-session, quantx-authenticator, and quantx-wallet
"""

from __future__ import annotations

from quantx_authenticator.push_authenticator import PushAuthenticator
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock
from quantx_wallet.backup_code_manager import BackupCodeManager
from quantx_wallet.device_linker import DeviceLinker


def test_sr_11_end_to_end_replay_rejection_across_credentials() -> None:
    clock = SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    shared_replay_store = InMemoryReplayStore(kv_store=kv_store)
    canonicalizer = JCSCanonicalizer()
    rate_limiter = InMemoryRateLimiter(kv_store=kv_store, clock=clock, limit=100, window_seconds=60)

    # 1. Push authenticator replay test
    push_auth = PushAuthenticator(
        rate_limiter=rate_limiter,
        replay_store=shared_replay_store,
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
    )
    push_rec = push_auth.issue("user@corp.internal")
    # First consume succeeds
    assert push_auth.consume(push_rec.approval_id) is True
    # Replay MUST fail
    assert push_auth.consume(push_rec.approval_id) is False

    # 2. Backup code single-use replay test
    bcm = BackupCodeManager(replay_store=shared_replay_store, kv_store=kv_store)
    code = "VALID-BACKUP-CODE-999"
    bcm.register_code("user@corp.internal", code)
    # First verification succeeds
    assert bcm.verify("user@corp.internal", code) is True
    # Replay MUST fail
    assert bcm.verify("user@corp.internal", code) is False

    # 3. Device linker token single-use replay test
    linker = DeviceLinker(
        replay_store=shared_replay_store,
        kv_store=kv_store,
        canonicalizer=canonicalizer,
        clock=clock,
    )
    token = linker.issue_pairing_token(subject_id="alice@corp.internal")
    # First link succeeds
    assert linker.consume_pairing_token(token) is True
    # Replay MUST fail
    assert linker.consume_pairing_token(token) is False
