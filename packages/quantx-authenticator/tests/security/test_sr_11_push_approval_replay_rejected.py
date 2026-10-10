"""Security test: SR-11 push approval replay rejection.

Layer: 5
Depends on: quantx_authenticator.push_authenticator.PushAuthenticator, conftest
Implements: Mandatory automated security test for SR-11 (push approval half)
Outside: Backup-code replay (handled in Layer 7 / quantx-wallet)
Inside: Atomic consume-once verification and replay rejection of push approval tokens
Security notes: SR-11: Push approvals are consumed through ReplayStore and can never be replayed.
"""

from __future__ import annotations

from typing import Any

from quantx_authenticator.push_authenticator import PushAuthenticator
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer


def test_sr_11_push_approval_replay_rejected(
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
    canonicalizer: JCSCanonicalizer,
) -> None:
    """SR-11: A consumed push approval cannot be replayed."""
    authenticator = PushAuthenticator(
        rate_limiter=rate_limiter,
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
        canonicalizer=canonicalizer,
        ttl_seconds=300,
    )

    record = authenticator.issue("charlie")

    # First consumption succeeds
    first_attempt = authenticator.consume(record.approval_id)
    assert first_attempt is True

    # Replay attempt fails unconditionally
    second_attempt = authenticator.consume(record.approval_id)
    assert second_attempt is False

    # Third replay attempt also fails
    third_attempt = authenticator.consume(record.approval_id)
    assert third_attempt is False
