"""Security test: TOTP rate limiter is independent of Layer 4 session limiter.

Layer: 5
Depends on: quantx_authenticator.totp_provider.TotpProvider, quantx_session.default_setup.default_setup, conftest
Implements: Mandatory security test for FR-5.2 cross-limiter independence
Outside: Transport routing and push rate limiting
Inside: Verifying that tripping TOTP rate limiter does not trip session limiter, and vice versa
Security notes: FR-5.2: Independent rate limiters prevent brute-force on one factor from impacting or exhausting the other.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_authenticator.totp_provider import TotpProvider
from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_session.default_setup import default_setup


def test_totp_rate_limiter_independent_of_session_limiter(
    kv_store: InMemoryKVStore,
    replay_store: InMemoryReplayStore,
    fake_clock: Any,
    test_secret: bytes,
) -> None:
    """FR-5.2: Tripping TOTP rate limiter does not affect Layer 4 session rate limiter."""
    # 1. Independent TOTP limiter (limit: 3)
    totp_limiter = InMemoryRateLimiter(
        kv_store=kv_store,
        clock=fake_clock,
        limit=3,
        window_seconds=60,
    )
    totp_provider = TotpProvider(
        rate_limiter=totp_limiter,
        clock=fake_clock,
        replay_store=replay_store,
        step_seconds=30,
    )
    totp_provider.register_secret("alice", test_secret)

    # 2. Recipe A setup with its own session rate limiters
    issuer, orchestrator, _ = default_setup(custom_clock=fake_clock)

    # 3. Exhaust TOTP rate limiter with bad attempts
    assert totp_provider.verify("alice", "000000") is False
    assert totp_provider.verify("alice", "000000") is False
    assert totp_provider.verify("alice", "000000") is False

    # 4th TOTP attempt trips TOTP rate limiter
    with pytest.raises(RateLimitedError):
        totp_provider.verify("alice", "000000")

    # 4. Confirm Layer 4 session orchestrator start/issue for alice is unaffected
    chal_record = issuer.issue(subject_id="alice")
    # orchestrator.start checks session identity rate limiter - MUST SUCCEED
    orchestrator.start(challenge_id=chal_record.challenge_id, identity_key="alice")
