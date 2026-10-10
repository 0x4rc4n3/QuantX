"""
Layer: 4
Depends on: session_orchestrator.py, Layer-0 ReplayStore/RateLimiter
Implements: Mandatory security tests 2 and 3 from 10-security-requirements.md, at the session-orchestrator level.
Outside: SR-10 mint-ordering — separate file.
Inside: Replay-after-consume and both limiters tripping independently.
Security notes: Mandatory tests 2 (replay rejection) and 3 (rate-limit rejection).
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.exceptions.rate_limited_error import RateLimitedError


def test_replay_rejection(session_fixture_bundle: dict[str, Any]) -> None:
    """Mandatory test 2: Consuming a challenge once succeeds; second attempt is rejected via ReplayStore."""
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    sign_challenge = bundle["sign_challenge"]

    record = issuer.issue(subject_id="alice", role_id="session-auth")
    signed_resp = sign_challenge(record.nonce)

    # First attempt succeeds
    token = orchestrator.finish(record.challenge_id, signed_resp)
    assert token is not None

    # Replay attempt fails closed
    with pytest.raises(MalformedInputError):
        # The key was deleted from kv_store and marked consumed in replay_store
        orchestrator.finish(record.challenge_id, signed_resp)


def test_rate_limit_per_identity_and_global_independence(
    session_fixture_bundle: dict[str, Any],
) -> None:
    """Mandatory test 3: Per-identity limiter and global limiter gate independently."""
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    sign_challenge = bundle["sign_challenge"]
    identity_rate_limiter = bundle["identity_rate_limiter"]
    global_rate_limiter = bundle["global_rate_limiter"]

    # 1. Per-identity limit trips while global is fine
    for _ in range(5):
        identity_rate_limiter.allow("dave")

    record_dave = issuer.issue(subject_id="dave", role_id="session-auth")
    signed_dave = sign_challenge(record_dave.nonce)
    with pytest.raises(RateLimitedError) as exc_info:
        orchestrator.finish(record_dave.challenge_id, signed_dave)
    assert "Identity rate limit exceeded" in str(exc_info.value)

    # Another user "eve" can still proceed because global limit is not tripped yet
    record_eve = issuer.issue(subject_id="eve", role_id="session-auth")
    signed_eve = sign_challenge(record_eve.nonce)
    token_eve = orchestrator.finish(record_eve.challenge_id, signed_eve)
    assert token_eve.subject_id == "eve"

    # 2. Exhaust global limiter (limit is 20)
    for _ in range(25):
        global_rate_limiter.allow("global")

    record_frank = issuer.issue(subject_id="frank", role_id="session-auth")
    signed_frank = sign_challenge(record_frank.nonce)
    with pytest.raises(RateLimitedError) as exc_info_global:
        orchestrator.finish(record_frank.challenge_id, signed_frank)
    assert "Global rate limit exceeded" in str(exc_info_global.value)
