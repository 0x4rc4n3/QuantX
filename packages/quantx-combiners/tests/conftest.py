"""
Layer: 2
Depends on: Layer-1 adapters, both combiner classes.
Implements: pytest fixtures.
Outside: Assertions themselves.
Inside: Fixture construction, including a genuine-hybrid-signature helper for the downgrade test to tamper with.
Security notes: The genuine-hybrid fixture is a precondition for test_sr_01_hybrid_downgrade_rejected.py and test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py being real tests rather than synthetic ones.
"""

from __future__ import annotations

import pytest
from quantx_combiners.kem.kem_combiner import KEMCombiner
from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import (
    SignatureCombiner,
    build_signed_payload,
)
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter


@pytest.fixture
def genuine_hybrid_signature_bundle():
    """
    Returns a bundle of initialized adapters, signers/verifiers,
    a genuine HYBRID wire signature, role_id, and message.
    """
    role_id = "role-hybrid-auth"
    message = b"hello-quantx-canonical-message"
    mode = Mode.HYBRID

    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    mldsa_priv, mldsa_pub = MlDsa65Adapter.generate_keypair()

    ed = Ed25519Adapter(private_key=ed_priv)
    mldsa = MlDsa65Adapter(private_key=mldsa_priv)

    verifiers = {
        "ed25519": ed,
        "ml-dsa-65": mldsa,
    }
    expected_algorithms = ["ed25519", "ml-dsa-65"]

    combiner = SignatureCombiner(
        required_mode=mode,
        role_id=role_id,
        expected_algorithms=expected_algorithms,
        verifiers=verifiers,
    )

    signed_payload = build_signed_payload(mode=mode, role_id=role_id, message=message)
    ed_sig = ed.sign(signed_payload)
    mldsa_sig = mldsa.sign(signed_payload)

    wire_bytes = signature_wire_format.encode(
        mode,
        [
            ("ed25519", ed_sig),
            ("ml-dsa-65", mldsa_sig),
        ],
    )

    return {
        "combiner": combiner,
        "wire_bytes": wire_bytes,
        "message": message,
        "role_id": role_id,
        "mode": mode,
        "ed_adapter": ed,
        "mldsa_adapter": mldsa,
        "ed_sig": ed_sig,
        "mldsa_sig": mldsa_sig,
    }


@pytest.fixture
def genuine_hybrid_kem_bundle():
    """
    Returns a bundle of initialized KEM adapters, combiner,
    public keys, private keys, encapsulated wire bytes, and honest shared secret.
    """
    mode = Mode.HYBRID
    x25519 = X25519Adapter()
    mlkem = MlKem768Adapter()

    x_priv, x_pub = X25519Adapter.generate_keypair()
    ml_priv, ml_pub = MlKem768Adapter.generate_keypair()

    providers = {
        "x25519": x25519,
        "ml-kem-768": mlkem,
    }
    expected_algorithms = ["x25519", "ml-kem-768"]

    combiner = KEMCombiner(
        required_mode=mode,
        expected_algorithms=expected_algorithms,
        providers=providers,
    )

    public_keys = {
        "x25519": x_pub,
        "ml-kem-768": ml_pub,
    }
    private_keys = {
        "x25519": x_priv,
        "ml-kem-768": ml_priv,
    }

    wire_bytes, honest_shared_secret = combiner.encapsulate(public_keys)

    return {
        "combiner": combiner,
        "wire_bytes": wire_bytes,
        "honest_shared_secret": honest_shared_secret,
        "public_keys": public_keys,
        "private_keys": private_keys,
        "x25519_adapter": x25519,
        "mlkem_adapter": mlkem,
    }
