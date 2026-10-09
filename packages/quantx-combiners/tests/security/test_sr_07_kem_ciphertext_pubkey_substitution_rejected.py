"""
Layer: 2
Depends on: The full KEM-combining path.
Implements: The mandatory automated security test for SR-7.
Outside: SR-1 (that's the signature-side test).
Inside: A genuine encapsulate/decapsulate round trip, then swapping the ciphertext or public key before decapsulation.
Security notes: This file IS the SR-7 enforcement check. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from typing import Any

from quantx_combiners.kem import kem_wire_format
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter


def test_sr_07_kem_ciphertext_substitution_rejected(
    genuine_hybrid_kem_bundle: dict[str, Any],
) -> None:
    """
    Mandatory test 4 (SR-7, 10-security-requirements.md):
    Swap the ciphertext post-encapsulation.
    Must fail, because ciphertext is bound into HKDF info.
    """
    bundle = genuine_hybrid_kem_bundle
    combiner = bundle["combiner"]
    wire_bytes = bundle["wire_bytes"]
    honest_secret = bundle["honest_shared_secret"]
    private_keys = bundle["private_keys"]

    mode, components = kem_wire_format.decode(wire_bytes)
    assert len(components) == 2

    # Generate a second independent encapsulation to get a valid alternate ciphertext
    alt_x25519 = X25519Adapter()
    alt_ct, _ = alt_x25519.encapsulate(components[0][1])

    # Substitute ciphertext on the classical leg
    tampered_components = [
        (components[0][0], components[0][1], alt_ct),
        components[1],
    ]
    tampered_wire = kem_wire_format.encode(mode, tampered_components)

    # Decapsulation with tampered ciphertext must either fail closed (b"") or yield a different secret
    result = combiner.decapsulate(tampered_wire, private_keys)
    assert result != honest_secret


def test_sr_07_kem_pubkey_substitution_rejected(
    genuine_hybrid_kem_bundle: dict[str, Any],
) -> None:
    """
    Mandatory test 4 (SR-7, 10-security-requirements.md):
    Swap the public key post-encapsulation.
    Must fail, because public key is bound into HKDF info.
    """
    bundle = genuine_hybrid_kem_bundle
    combiner = bundle["combiner"]
    wire_bytes = bundle["wire_bytes"]
    honest_secret = bundle["honest_shared_secret"]
    private_keys = bundle["private_keys"]

    mode, components = kem_wire_format.decode(wire_bytes)
    assert len(components) == 2

    # Substitute public key on the classical leg
    _, alt_pub = X25519Adapter.generate_keypair()

    tampered_components = [
        (components[0][0], alt_pub, components[0][2]),
        components[1],
    ]
    tampered_wire = kem_wire_format.encode(mode, tampered_components)

    # Decapsulation with tampered public key must fail or yield a different secret
    result = combiner.decapsulate(tampered_wire, private_keys)
    assert result != honest_secret
