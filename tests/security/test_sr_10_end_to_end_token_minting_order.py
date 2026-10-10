"""End-to-end security test for SR-10: Token minting order enforces mint-last invariant.

Layer: cross-cutting
Depends on: quantx_session.session_orchestrator.SessionOrchestrator, quantx_authenticator.totp_provider.TotpProvider, quantx_core.exceptions.MalformedInputError
Implements: Mandatory full-stack end-to-end test for SR-10 (token never minted before all gates succeed)
Outside: Every other numbered SR item
Inside: Fail second factor deliberately after primary factor succeeds, confirming no session token is stored
Wire format: SessionToken byte structures
Security notes: Mandatory SR-10 end-to-end confirmation across quantx-session and quantx-authenticator
"""

from __future__ import annotations

import pytest
from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import SignatureCombiner, build_signed_payload
from quantx_core.exceptions import MalformedInputError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_session.session_orchestrator import SessionOrchestrator


class MockTotpGate:
    """Mock TOTP gate that deliberately fails verification."""

    factor_name: str = "totp"

    def verify_factor(self, subject_id: str, payload: str | None) -> bool:
        return False


def test_sr_10_end_to_end_token_never_minted_on_second_factor_failure() -> None:
    clock = SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    rate_limiter = InMemoryRateLimiter(kv_store=kv_store, clock=clock, limit=100, window_seconds=60)
    canonicalizer = JCSCanonicalizer()

    # Setup hybrid verifiers
    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    ml_priv, ml_pub = MlDsa65Adapter.generate_keypair()

    combiner = SignatureCombiner(
        required_mode=Mode.HYBRID,
        role_id="session-auth",
        expected_algorithms=["ed25519", "ml-dsa-65"],
        verifiers={
            "ed25519": Ed25519Adapter(public_key=ed_pub),
            "ml-dsa-65": MlDsa65Adapter(public_key=ml_pub),
        },
    )

    issuer = ChallengeIssuer(
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        role_modes={"session-auth": Mode.HYBRID},
    )

    # Wire orchestrator with a failing second factor gate
    totp_gate = MockTotpGate()
    orchestrator = SessionOrchestrator(
        kv_store=kv_store,
        replay_store=replay_store,
        identity_rate_limiter=rate_limiter,
        global_rate_limiter=rate_limiter,
        clock=clock,
        combiners_by_role={"session-auth": combiner},
        second_factor_gates=[totp_gate],
    )

    # Issue challenge
    rec = issuer.issue(role_id="session-auth", subject_id="bob@corp.internal")
    chal_id = rec.challenge_id

    # Construct genuine valid hybrid primary-factor signature
    ed_signer = Ed25519Adapter(private_key=ed_priv)
    ml_signer = MlDsa65Adapter(private_key=ml_priv)
    payload_to_sign = build_signed_payload(
        mode=Mode.HYBRID, role_id="session-auth", message=rec.nonce
    )
    ed_sig = ed_signer.sign(payload_to_sign)
    ml_sig = ml_signer.sign(payload_to_sign)
    valid_wire_sig = signature_wire_format.encode(
        Mode.HYBRID, [("ed25519", ed_sig), ("ml-dsa-65", ml_sig)]
    )

    # Finish flow with valid primary factor, but failing second factor
    with pytest.raises(MalformedInputError, match="Second factor 'totp' verification failed"):
        orchestrator.finish(
            challenge_id=chal_id,
            signed_response=valid_wire_sig,
            second_factor_payloads={"totp": "wrong_code"},
        )

    # CRITICAL: Confirm NO session token was minted anywhere in kv_store (SR-10)
    for key in list(kv_store._store.keys()):
        assert not key.startswith("session:"), f"Leaked session token found: {key}"
