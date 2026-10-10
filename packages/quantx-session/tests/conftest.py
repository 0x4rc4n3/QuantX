"""
Layer: 4
Depends on: This package's src/ plus Layer 0-2.
Implements: pytest fixtures.
Outside: Assertions.
Inside: Fixture construction: fake Clock, real Layer 0-2 components, wired orchestrator and issuer.
Security notes: The fake Clock fixture is a precondition for deterministic expiry/rate-limit testing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import (
    SignatureCombiner,
    build_signed_payload,
)
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_session.session_orchestrator import SessionOrchestrator


class FakeClock(Clock):
    """Deterministic fake clock for testing TTL and rate limit windows."""

    def __init__(self, initial_time: datetime | None = None) -> None:
        self._current_time = initial_time or datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._current_time

    def advance(self, seconds: float) -> None:
        self._current_time += timedelta(seconds=seconds)

    def set_time(self, new_time: datetime) -> None:
        self._current_time = new_time


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def session_fixture_bundle(fake_clock: FakeClock) -> dict[str, Any]:
    role_id = "session-auth"
    mode = Mode.HYBRID

    # Keypairs for signers and verifiers
    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    mldsa_priv, mldsa_pub = MlDsa65Adapter.generate_keypair()

    ed_signer = Ed25519Adapter(private_key=ed_priv)
    mldsa_signer = MlDsa65Adapter(private_key=mldsa_priv)

    ed_verifier = Ed25519Adapter(public_key=ed_pub)
    mldsa_verifier = MlDsa65Adapter(public_key=mldsa_pub)

    verifiers = {
        "ed25519": ed_verifier,
        "ml-dsa-65": mldsa_verifier,
    }

    combiner = SignatureCombiner(
        required_mode=mode,
        role_id=role_id,
        expected_algorithms=["ed25519", "ml-dsa-65"],
        verifiers=verifiers,
    )

    kv_store = InMemoryKVStore(clock=fake_clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    identity_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store, clock=fake_clock, limit=5, window_seconds=60
    )
    global_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store, clock=fake_clock, limit=20, window_seconds=60
    )
    canonicalizer = JCSCanonicalizer()

    issuer = ChallengeIssuer(
        kv_store=kv_store,
        clock=fake_clock,
        canonicalizer=canonicalizer,
        role_modes={role_id: mode},
    )

    orchestrator = SessionOrchestrator(
        kv_store=kv_store,
        replay_store=replay_store,
        identity_rate_limiter=identity_rate_limiter,
        global_rate_limiter=global_rate_limiter,
        clock=fake_clock,
        combiners_by_role={role_id: combiner},
        session_ttl_seconds=3600,
    )

    def sign_challenge(nonce: bytes) -> bytes:
        payload = build_signed_payload(mode=mode, role_id=role_id, message=nonce)
        sig1 = ed_signer.sign(payload)
        sig2 = mldsa_signer.sign(payload)
        return signature_wire_format.encode(mode, [("ed25519", sig1), ("ml-dsa-65", sig2)])

    return {
        "issuer": issuer,
        "orchestrator": orchestrator,
        "clock": fake_clock,
        "kv_store": kv_store,
        "replay_store": replay_store,
        "identity_rate_limiter": identity_rate_limiter,
        "global_rate_limiter": global_rate_limiter,
        "sign_challenge": sign_challenge,
        "role_id": role_id,
        "mode": mode,
        "combiner": combiner,
    }
