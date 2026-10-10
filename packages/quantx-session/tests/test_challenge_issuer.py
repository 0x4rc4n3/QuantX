"""
Layer: 4
Depends on: challenge_issuer.py
Implements: pytest test functions.
Outside: Session orchestration itself.
Inside: Challenge issuance and storage behavior.
Security notes: Confirms FR-4.1/SR-1 at the issuance boundary.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.types.mode import Mode
from quantx_session.challenge_record import ChallengeRecord


def test_challenge_issuer_basic(session_fixture_bundle: dict[str, Any]) -> None:
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    kv_store = bundle["kv_store"]
    clock = bundle["clock"]

    subject_id = "user_alice"
    record = issuer.issue(subject_id=subject_id, role_id="session-auth", ttl_seconds=300)

    assert record.subject_id == subject_id
    assert record.role_id == "session-auth"
    assert record.required_mode == Mode.HYBRID
    assert record.issued_at == clock.now()
    assert (record.expires_at - record.issued_at).total_seconds() == 300
    assert len(record.nonce) > 0

    # Retrievable from KeyValueStore
    raw_stored = kv_store.get(f"challenge:{record.challenge_id}")
    assert raw_stored is not None
    restored = ChallengeRecord.from_json(raw_stored.decode("utf-8"))
    assert restored.challenge_id == record.challenge_id
    assert restored.nonce == record.nonce


def test_challenge_issuer_unknown_role(session_fixture_bundle: dict[str, Any]) -> None:
    bundle = session_fixture_bundle
    issuer = bundle["issuer"]
    with pytest.raises(ValueError):
        issuer.issue(subject_id="alice", role_id="nonexistent-role")
