"""End-to-end security test for SR-1: Hybrid downgrade rejection across full stack.

Layer: cross-cutting
Depends on: quantx_combiners.signature.signature_wire_format, quantx_session.default_setup, quantx_core.types.mode.Mode
Implements: Mandatory full-stack end-to-end test for SR-1 (downgrade to CLASSICAL_ONLY rejected)
Outside: Every other numbered SR item
Inside: Strip PQC component from genuine hybrid signature and rewrite mode byte, at full default_setup() -> start() -> finish() flow
Wire format: Signature wire format bytes
Security notes: Mandatory SR-1 end-to-end confirmation across quantx-combiners and quantx-session
"""

from __future__ import annotations

import pytest
from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import build_signed_payload
from quantx_core.exceptions import MalformedInputError
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_session.default_setup import default_setup


def test_sr_01_end_to_end_hybrid_downgrade_rejected() -> None:
    # 1. Setup full Recipe A stack
    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    ml_priv, ml_pub = MlDsa65Adapter.generate_keypair()

    custom_verifiers = {
        "session-auth": {
            "classical": Ed25519Adapter(public_key=ed_pub),
            "pqc": MlDsa65Adapter(public_key=ml_pub),
        }
    }

    issuer, orchestrator, _ = default_setup(custom_verifiers_by_role=custom_verifiers)

    # 2. Issue challenge for HYBRID role
    record = issuer.issue(role_id="session-auth", subject_id="alice@quantx.internal")
    challenge_id = record.challenge_id
    nonce = record.nonce

    # 3. Attacker strips PQC component, signs classical only, rewrites wire mode byte to CLASSICAL_ONLY
    ed_signer = Ed25519Adapter(private_key=ed_priv)
    payload = build_signed_payload(mode=Mode.CLASSICAL_ONLY, role_id="session-auth", message=nonce)
    classical_sig = ed_signer.sign(payload)
    downgraded_wire_sig = signature_wire_format.encode(
        Mode.CLASSICAL_ONLY, [("ed25519", classical_sig)]
    )

    # 4. Orchestrator finish must fail end-to-end with MalformedInputError
    orchestrator.start(challenge_id=challenge_id, identity_key="alice@quantx.internal")
    with pytest.raises(MalformedInputError):
        orchestrator.finish(challenge_id=challenge_id, signed_response=downgraded_wire_sig)
