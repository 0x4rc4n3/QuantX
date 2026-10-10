"""Security test: SR-5 push issuance rate-limited before send.

Layer: 5
Depends on: quantx_authenticator.push_authenticator.PushAuthenticator, conftest
Implements: Mandatory automated security test for SR-5
Outside: Push delivery network mechanics
Inside: Confirming that rate limiting trips before invoking the send callback
Security notes: SR-5: Push-notification issuance is rate-limited before sending to prevent push fatigue attacks.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_authenticator.push_approval_record import PushApprovalRecord
from quantx_authenticator.push_authenticator import PushAuthenticator
from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer


def test_sr_05_push_issuance_rate_limited_before_send(
    replay_store: InMemoryReplayStore,
    kv_store: InMemoryKVStore,
    fake_clock: Any,
    canonicalizer: JCSCanonicalizer,
) -> None:
    """SR-5: Exceeding push limit rejects immediately without invoking send_fn."""
    # Strict limit: 2 requests per window
    strict_limiter = InMemoryRateLimiter(
        kv_store=kv_store,
        clock=fake_clock,
        limit=2,
        window_seconds=60,
    )

    send_call_count = 0

    def mock_send_fn(rec: PushApprovalRecord) -> None:
        nonlocal send_call_count
        send_call_count += 1

    authenticator = PushAuthenticator(
        rate_limiter=strict_limiter,
        replay_store=replay_store,
        kv_store=kv_store,
        clock=fake_clock,
        canonicalizer=canonicalizer,
        ttl_seconds=300,
        send_fn=mock_send_fn,
    )

    # First two requests succeed and trigger send_fn
    authenticator.issue("alice")
    assert send_call_count == 1
    authenticator.issue("alice")
    assert send_call_count == 2

    # Third request exceeds limit: must raise RateLimitedError
    with pytest.raises(RateLimitedError):
        authenticator.issue("alice")

    # Send function must NOT have been called on the rejected attempt (SR-5)
    assert send_call_count == 2
