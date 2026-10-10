"""Unit tests for PushAuthenticator.

Layer: 5
Depends on: quantx_authenticator.push_authenticator.PushAuthenticator, conftest
Implements: Pytest tests validating genuine push issuance and consume-once verification
Outside: External push delivery network calls
Inside: Push approval generation, expiration checking, and genuine consume lifecycle
Security notes: Confirms that genuine push approvals succeed once and expire correctly.
"""

from __future__ import annotations

from typing import Any

from quantx_authenticator.push_authenticator import PushAuthenticator
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer


def test_push_issue_and_consume_success(
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
    canonicalizer: JCSCanonicalizer,
) -> None:
    """A genuine push approval is issued and consumed successfully."""
    authenticator = PushAuthenticator(
        rate_limiter=rate_limiter,
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
        canonicalizer=canonicalizer,
        ttl_seconds=300,
    )

    record = authenticator.issue("alice")
    assert record.subject_id == "alice"
    assert record.approval_id.startswith("push_")

    # Consume once
    assert authenticator.consume(record.approval_id) is True

    # Re-consume fails
    assert authenticator.consume(record.approval_id) is False


def test_push_expired_fails(
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
    canonicalizer: JCSCanonicalizer,
) -> None:
    """An expired push approval cannot be consumed."""
    authenticator = PushAuthenticator(
        rate_limiter=rate_limiter,
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
        canonicalizer=canonicalizer,
        ttl_seconds=300,
    )

    record = authenticator.issue("bob")
    # Advance clock past TTL (301 seconds)
    fake_clock.advance(301)

    assert authenticator.consume(record.approval_id) is False
