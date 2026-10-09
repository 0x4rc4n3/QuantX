"""
Layer: 2
Depends on: kem_combiner.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies correct derivation across all modes and validates V2 §11 HKDF smoke vector.
"""

from __future__ import annotations

from typing import Any

from quantx_combiners.kem import kem_hkdf_binding
from quantx_combiners.kem.kem_combiner import KEMCombiner
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter


def test_one_component_hkdf_binding_smoke_vector() -> None:
    """
    Test normative smoke vector from V2 §11:
    Shared secret: 101112131415161718191a1b1c1d1e1f
    Algorithm: x25519
    Public key: aabb
    Ciphertext: 010203
    Expected result: eb43f2e06a96f73985f6094525595cc8a68e8036352724ddc54e516e2963e025
    """
    shared_secret = bytes.fromhex("101112131415161718191a1b1c1d1e1f")
    components = [("x25519", bytes.fromhex("aabb"), bytes.fromhex("010203"))]
    derived = kem_hkdf_binding.derive([shared_secret], components)
    assert derived.hex() == "eb43f2e06a96f73985f6094525595cc8a68e8036352724ddc54e516e2963e025"


def test_kem_combiner_hybrid(genuine_hybrid_kem_bundle: dict[str, Any]) -> None:
    bundle = genuine_hybrid_kem_bundle
    combiner = bundle["combiner"]
    wire_bytes = bundle["wire_bytes"]
    honest_secret = bundle["honest_shared_secret"]
    private_keys = bundle["private_keys"]

    # Decapsulate recovers exact matching honest shared secret
    decapsulated = combiner.decapsulate(wire_bytes, private_keys)
    assert decapsulated == honest_secret
    assert len(decapsulated) == 32


def test_kem_combiner_pqc_only() -> None:
    mlkem = MlKem768Adapter()
    combiner = KEMCombiner(
        required_mode=Mode.PQC_ONLY,
        expected_algorithms=["ml-kem-768"],
        providers={"ml-kem-768": mlkem},
    )

    ml_priv, ml_pub = MlKem768Adapter.generate_keypair()
    pub_keys = {"ml-kem-768": ml_pub}
    wire_bytes, secret = combiner.encapsulate(pub_keys)

    assert len(secret) == 32
    decapsulated = combiner.decapsulate(wire_bytes, {"ml-kem-768": ml_priv})
    assert decapsulated == secret


def test_kem_combiner_classical_only() -> None:
    x25519 = X25519Adapter()
    combiner = KEMCombiner(
        required_mode=Mode.CLASSICAL_ONLY,
        expected_algorithms=["x25519"],
        providers={"x25519": x25519},
    )

    x_priv, x_pub = X25519Adapter.generate_keypair()
    pub_keys = {"x25519": x_pub}
    wire_bytes, secret = combiner.encapsulate(pub_keys)

    assert len(secret) == 32
    decapsulated = combiner.decapsulate(wire_bytes, {"x25519": x_priv})
    assert decapsulated == secret
