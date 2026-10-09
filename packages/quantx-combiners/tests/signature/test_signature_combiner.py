"""
Layer: 2
Depends on: signature_combiner.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies correct orchestration and fail-closed behavior across all modes.
"""

from __future__ import annotations

from typing import Any

from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import (
    SignatureCombiner,
    build_signed_payload,
)
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ecdsa_p256_adapter import EcdsaP256Adapter
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter


def test_signature_combiner_hybrid(
    genuine_hybrid_signature_bundle: dict[str, Any],
) -> None:
    bundle = genuine_hybrid_signature_bundle
    combiner = bundle["combiner"]
    wire_bytes = bundle["wire_bytes"]
    message = bundle["message"]

    # Honest verification succeeds
    assert combiner.verify(wire_bytes, message) is True

    # Tampered message fails
    assert combiner.verify(wire_bytes, b"tampered-message") is False

    # Corrupted wire bytes fails
    corrupted_bytes = bytearray(wire_bytes)
    corrupted_bytes[-1] ^= 0xFF
    assert combiner.verify(bytes(corrupted_bytes), message) is False


def test_signature_combiner_pqc_only() -> None:
    mode = Mode.PQC_ONLY
    role_id = "role-pqc"
    message = b"pqc-only-message"

    priv, pub = MlDsa65Adapter.generate_keypair()
    mldsa = MlDsa65Adapter(private_key=priv)
    verifiers = {"ml-dsa-65": mldsa}
    combiner = SignatureCombiner(
        required_mode=mode,
        role_id=role_id,
        expected_algorithms=["ml-dsa-65"],
        verifiers=verifiers,
    )

    signed_payload = build_signed_payload(mode=mode, role_id=role_id, message=message)
    sig = mldsa.sign(signed_payload)
    wire_bytes = signature_wire_format.encode(mode, [("ml-dsa-65", sig)])

    assert combiner.verify(wire_bytes, message) is True
    assert combiner.verify(wire_bytes, b"bad") is False


def test_signature_combiner_classical_only() -> None:
    mode = Mode.CLASSICAL_ONLY
    role_id = "role-classical"
    message = b"classical-only-message"

    priv, pub = EcdsaP256Adapter.generate_keypair()
    ecdsa = EcdsaP256Adapter(private_key=priv)
    verifiers = {"ecdsa-p256": ecdsa}
    combiner = SignatureCombiner(
        required_mode=mode,
        role_id=role_id,
        expected_algorithms=["ecdsa-p256"],
        verifiers=verifiers,
    )

    signed_payload = build_signed_payload(mode=mode, role_id=role_id, message=message)
    sig = ecdsa.sign(signed_payload)
    wire_bytes = signature_wire_format.encode(mode, [("ecdsa-p256", sig)])

    assert combiner.verify(wire_bytes, message) is True
    assert combiner.verify(wire_bytes, b"wrong-message") is False


def test_signature_combiner_one_leg_invalid_fails_hybrid() -> None:
    role_id = "role-hybrid-auth"
    message = b"hybrid-message"
    mode = Mode.HYBRID

    ed_priv, _ = Ed25519Adapter.generate_keypair()
    mldsa_priv, _ = MlDsa65Adapter.generate_keypair()
    ed = Ed25519Adapter(private_key=ed_priv)
    mldsa = MlDsa65Adapter(private_key=mldsa_priv)

    combiner = SignatureCombiner(
        required_mode=mode,
        role_id=role_id,
        expected_algorithms=["ed25519", "ml-dsa-65"],
        verifiers={"ed25519": ed, "ml-dsa-65": mldsa},
    )

    signed_payload = build_signed_payload(mode=mode, role_id=role_id, message=message)
    ed_sig = ed.sign(signed_payload)
    # Give a bogus signature for ml-dsa
    fake_mldsa_sig = b"\x00" * 3309

    wire_bytes = signature_wire_format.encode(
        mode,
        [("ed25519", ed_sig), ("ml-dsa-65", fake_mldsa_sig)],
    )

    # Hybrid AND rule: both must pass. Because PQC fails, overall result must be False.
    assert combiner.verify(wire_bytes, message) is False
