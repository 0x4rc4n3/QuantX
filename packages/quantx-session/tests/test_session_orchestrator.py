"""
Layer: 4
Depends on: session_orchestrator.py
Implements: pytest test functions.
Outside: The SR-10 mint-ordering adversarial test and the replay/rate-limit test — separate files in security/.
Inside: Genuine-path finish()/validate() behavior.
Security notes: Verifies primary factor gating and session token validation.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError


def test_session_orchestrator_finish_and_validate(session_fixture_bundle: dict[str, Any]) -> None:
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    sign_challenge = bundle["sign_challenge"]

    # 1. Issue challenge
    record = issuer.issue(subject_id="alice", role_id="session-auth")

    # 2. Sign challenge nonce
    signed_resp = sign_challenge(record.nonce)

    # 3. Finish session flow
    token = orchestrator.finish(challenge_id=record.challenge_id, signed_response=signed_resp)
    assert token.subject_id == "alice"
    assert "primary" in token.factors_completed

    # 4. Validate token
    assert orchestrator.validate(token) is True
    assert orchestrator.validate(token.token_id) is True

    # 5. Challenge should now be consumed / deleted
    with pytest.raises(MalformedInputError):
        orchestrator.finish(challenge_id=record.challenge_id, signed_response=signed_resp)


def test_session_orchestrator_tampered_signature_fails(
    session_fixture_bundle: dict[str, Any],
) -> None:
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    orchestrator = bundle["orchestrator"]
    sign_challenge = bundle["sign_challenge"]

    record = issuer.issue(subject_id="bob", role_id="session-auth")
    signed_resp = bytearray(sign_challenge(record.nonce))
    signed_resp[-1] ^= 0xFF

    with pytest.raises(MalformedInputError) as exc_info:
        orchestrator.finish(challenge_id=record.challenge_id, signed_response=bytes(signed_resp))
    assert "verification failed" in str(exc_info.value)
