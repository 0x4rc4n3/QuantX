"""Unit tests for TotpProvider.

Layer: 5
Depends on: quantx_authenticator.totp_provider.TotpProvider, conftest
Implements: Pytest tests validating RFC 6238 test vectors, drift windows, and replay prevention
Outside: Counter-based HOTP verification
Inside: RFC 6238 time vectors, drift allowance (+/- 1 step), step consumption, and invalid code rejection
Security notes: Verifies time-based code verification and D-015 step single-use consumption.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from quantx_authenticator.totp_provider import TotpProvider
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore

RFC_6238_VECTORS = [
    (59, "287082"),
    (1111111109, "081804"),
    (1111111111, "050471"),
    (1234567890, "005924"),
    (2000000000, "279037"),
]


def test_rfc_6238_test_vectors(
    fake_clock: Any,
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    test_secret: bytes,
) -> None:
    """Validate official RFC 6238 test vectors for HMAC-SHA1 6-digit TOTP."""
    provider = TotpProvider(
        rate_limiter=rate_limiter,
        clock=fake_clock,
        replay_store=replay_store,
        step_seconds=30,
        digits=6,
        allowed_drift_steps=1,
    )
    provider.register_secret("alice", test_secret)

    for timestamp, expected_code in RFC_6238_VECTORS:
        fake_clock.set_time(datetime.fromtimestamp(timestamp, tz=timezone.utc))
        code = provider.generate_code("alice")
        assert code == expected_code, f"Failed at timestamp {timestamp}"
        assert provider.verify("alice", expected_code) is True


def test_totp_replay_prevention_same_step(
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    fake_clock: Any,
    test_secret: bytes,
) -> None:
    """A TOTP code cannot be reused within the same time step window (D-015)."""
    provider = TotpProvider(
        rate_limiter=rate_limiter,
        clock=fake_clock,
        replay_store=replay_store,
        step_seconds=30,
    )
    provider.register_secret("bob", test_secret)

    code = provider.generate_code("bob")
    # First verification succeeds
    assert provider.verify("bob", code) is True

    # Immediate second verification within same window fails closed (step already consumed)
    assert provider.verify("bob", code) is False


def test_totp_drift_window(
    rate_limiter: InMemoryRateLimiter,
    replay_store: InMemoryReplayStore,
    fake_clock: Any,
    test_secret: bytes,
) -> None:
    """Accepts codes for current, -1, and +1 steps; rejects >= 2 steps away."""
    provider = TotpProvider(
        rate_limiter=rate_limiter,
        clock=fake_clock,
        replay_store=replay_store,
        step_seconds=30,
        allowed_drift_steps=1,
    )
    provider.register_secret("carol", test_secret)

    # Past code (-30s) succeeds
    past_code = provider.generate_code("carol", offset_seconds=-30)
    assert provider.verify("carol", past_code) is True

    # Future code (+30s) succeeds
    future_code = provider.generate_code("carol", offset_seconds=30)
    assert provider.verify("carol", future_code) is True

    # Far future code (+60s, 2 steps away) fails
    far_code = provider.generate_code("carol", offset_seconds=60)
    assert provider.verify("carol", far_code) is False
