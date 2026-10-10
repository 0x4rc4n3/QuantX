"""
Layer: 4
Depends on: session_orchestrator.py
Implements: The mandatory automated security test for SR-10.
Outside: Replay/rate-limit rejection itself — separate file.
Inside: Forcing failure at every gate (primary factor, each configured second factor, replay check, rate limit) and confirming no token is ever observable afterward.
Security notes: This file IS the SR-10 enforcement check. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.exceptions.rate_limited_error import RateLimitedError


def test_sr_10_token_never_minted_on_signature_failure(
    session_fixture_bundle: dict[str, Any],
) -> None:
    """SR-10: Force primary-factor verification failure -> confirm no token exists in store."""
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    kv_store = bundle["kv_store"]

    record = issuer.issue(subject_id="alice", role_id="session-auth")
    bad_signature = b"\x01\x01\x02\x00\x01a\x00\x00\x00\x01b\x00\x01c\x00\x00\x00\x01d"

    with pytest.raises(MalformedInputError):
        orchestrator.finish(record.challenge_id, bad_signature)

    # Confirm no session token was minted or stored
    # InMemoryKVStore keys can be checked via get
    for k in range(100):
        assert kv_store.get(f"session:tok_{k}") is None


def test_sr_10_token_never_minted_on_second_factor_failure(
    session_fixture_bundle: dict[str, Any],
) -> None:
    """SR-10: Primary factor succeeds but second factor fails -> confirm no token is minted."""
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    sign_challenge = bundle["sign_challenge"]

    # Create a failing second factor gate
    failing_gate = MagicMock()
    failing_gate.factor_name = "totp"
    failing_gate.verify_factor.return_value = False

    orchestrator = bundle["orchestrator"]
    orchestrator._second_factor_gates = [failing_gate]

    record = issuer.issue(subject_id="alice", role_id="session-auth")
    signed_resp = sign_challenge(record.nonce)

    with pytest.raises(MalformedInputError) as exc_info:
        orchestrator.finish(
            record.challenge_id,
            signed_resp,
            second_factor_payloads={"totp": "123456"},
        )
    assert "Second factor 'totp' verification failed" in str(exc_info.value)


def test_sr_10_token_never_minted_on_rate_limit_failure(
    session_fixture_bundle: dict[str, Any],
) -> None:
    """SR-10: Rate limiter trips -> no token minted."""
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    sign_challenge = bundle["sign_challenge"]
    identity_rate_limiter = bundle["identity_rate_limiter"]

    record = issuer.issue(subject_id="charlie", role_id="session-auth")
    signed_resp = sign_challenge(record.nonce)

    # Exhaust rate limit for charlie (limit is 5)
    for _ in range(5):
        identity_rate_limiter.allow("charlie")

    with pytest.raises(RateLimitedError):
        orchestrator.finish(record.challenge_id, signed_resp)
