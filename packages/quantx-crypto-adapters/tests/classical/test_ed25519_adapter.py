"""
Layer: 1
Depends on: quantx_crypto_adapters.classical.ed25519_adapter.Ed25519Adapter
Implements: pytest test functions for Ed25519Adapter
Outside: Testing any other adapter.
Inside: Ed25519 round-trip, tampered signature rejection, and wrong key verification.
Security notes: Non-security unit test; fail-closed malformed test is in security suite.
"""

from __future__ import annotations

from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter


def test_ed25519_adapter_roundtrip(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = Ed25519Adapter.generate_keypair()
    signer = Ed25519Adapter(private_key=priv_bytes)
    verifier = Ed25519Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert len(sig) == 64
    assert verifier.verify(sample_message, sig) is True


def test_ed25519_adapter_tampered_signature_fails(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = Ed25519Adapter.generate_keypair()
    signer = Ed25519Adapter(private_key=priv_bytes)
    verifier = Ed25519Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    # Flip one byte
    tampered_sig = bytearray(sig)
    tampered_sig[0] ^= 0xFF
    assert verifier.verify(sample_message, bytes(tampered_sig)) is False


def test_ed25519_adapter_wrong_message_fails(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = Ed25519Adapter.generate_keypair()
    signer = Ed25519Adapter(private_key=priv_bytes)
    verifier = Ed25519Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(b"different message", sig) is False


def test_ed25519_adapter_wrong_key_fails(sample_message: bytes) -> None:
    priv_bytes, _ = Ed25519Adapter.generate_keypair()
    _, other_pub_bytes = Ed25519Adapter.generate_keypair()

    signer = Ed25519Adapter(private_key=priv_bytes)
    verifier = Ed25519Adapter(public_key=other_pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(sample_message, sig) is False
