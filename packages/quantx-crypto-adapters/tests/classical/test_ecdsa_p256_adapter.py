"""
Layer: 1
Depends on: quantx_crypto_adapters.classical.ecdsa_p256_adapter.EcdsaP256Adapter
Implements: pytest test functions for EcdsaP256Adapter
Outside: Testing any other adapter.
Inside: ECDSA-P256 round-trip, tampered signature rejection, and wrong key verification.
Security notes: Non-security unit test; fail-closed malformed test is in security suite.
"""

from __future__ import annotations

from quantx_crypto_adapters.classical.ecdsa_p256_adapter import EcdsaP256Adapter


def test_ecdsa_p256_adapter_roundtrip(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = EcdsaP256Adapter.generate_keypair()
    signer = EcdsaP256Adapter(private_key=priv_bytes)
    verifier = EcdsaP256Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert len(sig) > 0
    assert verifier.verify(sample_message, sig) is True


def test_ecdsa_p256_adapter_tampered_signature_fails(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = EcdsaP256Adapter.generate_keypair()
    signer = EcdsaP256Adapter(private_key=priv_bytes)
    verifier = EcdsaP256Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    tampered_sig = bytearray(sig)
    tampered_sig[-1] ^= 0xFF
    assert verifier.verify(sample_message, bytes(tampered_sig)) is False


def test_ecdsa_p256_adapter_wrong_message_fails(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = EcdsaP256Adapter.generate_keypair()
    signer = EcdsaP256Adapter(private_key=priv_bytes)
    verifier = EcdsaP256Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(b"different message", sig) is False


def test_ecdsa_p256_adapter_wrong_key_fails(sample_message: bytes) -> None:
    priv_bytes, _ = EcdsaP256Adapter.generate_keypair()
    _, other_pub_bytes = EcdsaP256Adapter.generate_keypair()

    signer = EcdsaP256Adapter(private_key=priv_bytes)
    verifier = EcdsaP256Adapter(public_key=other_pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(sample_message, sig) is False
