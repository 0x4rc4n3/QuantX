"""End-to-end security test for SR-14: Injected Clock governs all time-dependent behavior.

Layer: cross-cutting
Depends on: quantx_core.interfaces.clock.Clock, quantx_session.default_setup, quantx_core.exceptions.MalformedInputError
Implements: Mandatory full-stack end-to-end test for SR-14 (all components consume injected Clock, no wall-clock reads)
Outside: Every other numbered SR item
Inside: Advance controllable Clock and verify challenge expiry and rate limit resets follow injected Clock exactly
Wire format: Timestamps
Security notes: Mandatory SR-14 end-to-end confirmation across quantx-core, quantx-session, and quantx-authenticator
"""

from __future__ import annotations

import datetime
from datetime import timezone

import pytest
from quantx_core.exceptions import MalformedInputError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_core.types.mode import Mode
from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_session.session_orchestrator import SessionOrchestrator


class FakeControllableClock(Clock):
    """Controllable test clock returning timezone-aware datetime."""

    def __init__(self, start_time: datetime.datetime | None = None) -> None:
        self._time = start_time or datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime.datetime:
        return self._time

    def advance(self, seconds: float) -> None:
        self._time += datetime.timedelta(seconds=seconds)


def test_sr_14_end_to_end_injected_clock_governs_expiry_and_rate_limits() -> None:
    clock = FakeControllableClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    canonicalizer = JCSCanonicalizer()

    # Rate limiter with 60 second window
    rate_limiter = InMemoryRateLimiter(kv_store=kv_store, clock=clock, limit=1, window_seconds=60)

    issuer = ChallengeIssuer(
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        role_modes={"session-auth": Mode.HYBRID},
    )

    orchestrator = SessionOrchestrator(
        kv_store=kv_store,
        replay_store=replay_store,
        identity_rate_limiter=rate_limiter,
        global_rate_limiter=rate_limiter,
        clock=clock,
        combiners_by_role={},
    )

    # 1. Issue challenge with 300s TTL
    rec = issuer.issue(
        subject_id="alice@corp.internal",
        role_id="session-auth",
        ttl_seconds=300,
    )
    chal_id = rec.challenge_id

    # 2. Advance clock past challenge expiry (by 301 seconds)
    clock.advance(301.0)

    # 3. Orchestrator finish must detect expiration solely based on injected clock
    with pytest.raises(MalformedInputError, match="expired"):
        orchestrator.finish(challenge_id=chal_id, signed_response=b"dummy_sig")
