"""
Layer: 4
Depends on: default_setup.py and everything it wires.
Implements: The mandatory Layer-4 done-criterion demo, as a test.
Outside: Recipe B/C — this test only exercises Recipe A.
Inside: The full four-call flow.
Security notes: Layer-4 done criterion: default_setup() -> start() -> finish() -> validate().
"""

from __future__ import annotations

from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import build_signed_payload
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_session.default_setup import default_setup


def test_default_setup_end_to_end_demo() -> None:
    # 1. Wire in-memory Recipe A setup
    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    mldsa_priv, mldsa_pub = MlDsa65Adapter.generate_keypair()

    ed_verifier = Ed25519Adapter(public_key=ed_pub)
    mldsa_verifier = MlDsa65Adapter(public_key=mldsa_pub)

    from quantx_core.interfaces.verifier import Verifier

    custom_verifiers: dict[str, dict[str, Verifier]] = {
        "session-auth": {
            "ed25519": ed_verifier,
            "ml-dsa-65": mldsa_verifier,
        }
    }

    issuer, orchestrator, registry = default_setup(custom_verifiers_by_role=custom_verifiers)

    # 2. Start / Issue challenge
    record = issuer.issue(subject_id="alice", role_id="session-auth")
    orchestrator.start(challenge_id=record.challenge_id, identity_key=record.subject_id)

    # 3. Client signs the challenge nonce with classical + PQC keys
    ed_signer = Ed25519Adapter(private_key=ed_priv)
    mldsa_signer = MlDsa65Adapter(private_key=mldsa_priv)

    payload = build_signed_payload(
        mode=Mode.HYBRID,
        role_id=record.role_id,
        message=record.nonce,
    )
    ed_sig = ed_signer.sign(payload)
    mldsa_sig = mldsa_signer.sign(payload)

    wire_response = signature_wire_format.encode(
        Mode.HYBRID,
        [("ed25519", ed_sig), ("ml-dsa-65", mldsa_sig)],
    )

    # 4. Finish session
    token = orchestrator.finish(challenge_id=record.challenge_id, signed_response=wire_response)
    assert token.subject_id == "alice"
    assert "primary" in token.factors_completed

    # 5. Validate session token
    assert orchestrator.validate(token) is True
    assert orchestrator.validate(token.token_id) is True
