"""Unit tests for HotpProvider.

Layer: 5
Depends on: quantx_authenticator.hotp_provider.HotpProvider, conftest
Implements: Pytest tests validating RFC 4226 test vectors, look-ahead window, and counter advancement
Outside: Time-based TOTP verification
Inside: Counter verification, look-ahead logic, and non-advancement upon failure
Security notes: Verifies that only valid codes advance counter state per D-015.
"""

from __future__ import annotations

from quantx_authenticator.hotp_provider import HotpProvider
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter

RFC_4226_VECTORS = [
    (0, "755224"),
    (1, "287082"),
    (2, "359152"),
    (3, "969429"),
    (4, "338314"),
    (5, "254676"),
    (6, "287922"),
    (7, "162583"),
    (8, "399871"),
    (9, "520489"),
]


def test_rfc_4226_test_vectors(
    rate_limiter: InMemoryRateLimiter,
    kv_store: InMemoryKVStore,
    test_secret: bytes,
) -> None:
    """Validate RFC 4226 official test vectors."""
    provider = HotpProvider(rate_limiter=rate_limiter, kv_store=kv_store, lookahead_window=10)
    provider.register_secret("alice", test_secret, initial_counter=0)

    for counter, expected_code in RFC_4226_VECTORS:
        generated = provider.generate_code("alice", counter_override=counter)
        assert generated == expected_code, f"Failed vector at counter {counter}"


def test_hotp_counter_advancement(
    rate_limiter: InMemoryRateLimiter,
    kv_store: InMemoryKVStore,
    test_secret: bytes,
) -> None:
    """Verifying a correct code increments the counter; invalid code does not advance counter."""
    provider = HotpProvider(rate_limiter=rate_limiter, kv_store=kv_store, lookahead_window=10)
    provider.register_secret("bob", test_secret, initial_counter=0)

    # 1. First code (C=0 -> 755224)
    assert provider.verify("bob", "755224") is True
    assert provider.get_counter("bob") == 1

    # 2. Invalid code fails and counter stays at 1
    assert provider.verify("bob", "000000") is False
    assert provider.get_counter("bob") == 1

    # 3. Look-ahead within window (say user skipped C=1 and entered C=3 -> 969429)
    assert provider.verify("bob", "969429") is True
    # Counter must advance past C=3 to 4
    assert provider.get_counter("bob") == 4
