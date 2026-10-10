"""End-to-end security test for SR-5: Push-notification issuance rate-limited before sending.

Layer: cross-cutting
Depends on: quantx_authenticator.push_authenticator.PushAuthenticator, quantx_session.default_setup, quantx_core.exceptions.RateLimitedError
Implements: Mandatory full-stack end-to-end test for SR-5 (push rate-limited before sending)
Outside: Every other numbered SR item
Inside: Drive PushAuthenticator in wired system and confirm rate limit trips before send attempt is made
Wire format: Push approval payload
Security notes: Mandatory SR-5 end-to-end confirmation across quantx-authenticator and quantx-session
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from quantx_authenticator.push_authenticator import PushAuthenticator
from quantx_core.exceptions import RateLimitedError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock


def test_sr_05_end_to_end_push_rate_limit_trips_before_send() -> None:
    clock = SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    # Rate limiter allowing only 2 push notifications per minute
    push_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store, clock=clock, limit=2, window_seconds=60
    )
    canonicalizer = JCSCanonicalizer()

    mock_send = MagicMock()
    push_auth = PushAuthenticator(
        rate_limiter=push_rate_limiter,
        replay_store=replay_store,
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        ttl_seconds=300,
        send_fn=mock_send,
    )

    # 1. First 2 requests succeed and invoke send
    rec1 = push_auth.issue("user@corp.internal")
    assert rec1 is not None
    assert mock_send.call_count == 1

    rec2 = push_auth.issue("user@corp.internal")
    assert rec2 is not None
    assert mock_send.call_count == 2

    # 2. 3rd request trips the rate limiter BEFORE send_fn is called
    with pytest.raises(RateLimitedError, match="rate limit exceeded"):
        push_auth.issue("user@corp.internal")

    # Call count MUST remain 2 (send_fn was never invoked on rate-limited attempt)
    assert mock_send.call_count == 2
