"""
Layer: 3
Depends on: registry_config_signature.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies JCS canonicalization and Ed25519 signature round-trip over config dictionaries.
"""

from __future__ import annotations

from typing import Any

from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_registry import registry_config_signature


def test_registry_config_signature_roundtrip() -> None:
    data = {
        "roles": [
            {
                "role_id": "session-auth",
                "mode": "HYBRID",
                "signature_algorithms": ["ed25519", "ml-dsa-65"],
                "kem_algorithms": ["x25519", "ml-kem-768"],
            }
        ]
    }

    priv, pub = Ed25519Adapter.generate_keypair()
    signer = Ed25519Adapter(private_key=priv)
    verifier = Ed25519Adapter(public_key=pub)
    canonicalizer = JCSCanonicalizer()

    sig = registry_config_signature.sign(data, signer, canonicalizer)
    assert len(sig) == 64

    # Valid verification
    assert registry_config_signature.verify(data, sig, verifier, canonicalizer) is True

    # Tampered config data
    tampered_data: dict[str, Any] = {
        "roles": [
            {
                "role_id": "session-auth",
                "mode": "CLASSICAL_ONLY",  # Tampered mode
                "signature_algorithms": ["ed25519"],
                "kem_algorithms": ["x25519"],
            }
        ]
    }
    assert registry_config_signature.verify(tampered_data, sig, verifier, canonicalizer) is False

    # Corrupted signature
    corrupted_sig = bytearray(sig)
    corrupted_sig[0] ^= 0xFF
    assert (
        registry_config_signature.verify(data, bytes(corrupted_sig), verifier, canonicalizer)
        is False
    )
