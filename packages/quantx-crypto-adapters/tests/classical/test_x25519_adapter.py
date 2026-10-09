"""
Layer: 1
Depends on: quantx_crypto_adapters.classical.x25519_adapter.X25519Adapter
Implements: pytest test functions for X25519Adapter
Outside: Testing any other adapter.
Inside: X25519 round-trip, tampered ciphertext, and wrong private key tests.
Security notes: Non-security unit test; fail-closed malformed test is in security suite.
"""

from __future__ import annotations

from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter


def test_x25519_adapter_roundtrip() -> None:
    priv_bytes, pub_bytes = X25519Adapter.generate_keypair()
    adapter = X25519Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    assert len(ciphertext) == 32
    assert len(shared_secret_enc) == 32

    shared_secret_dec = adapter.decapsulate(ciphertext, priv_bytes)
    assert shared_secret_dec == shared_secret_enc


def test_x25519_adapter_tampered_ciphertext() -> None:
    priv_bytes, pub_bytes = X25519Adapter.generate_keypair()
    adapter = X25519Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    tampered_ct = bytearray(ciphertext)
    tampered_ct[0] ^= 0xFF

    shared_secret_dec = adapter.decapsulate(bytes(tampered_ct), priv_bytes)
    # DH with different point yields different shared secret
    assert shared_secret_dec != shared_secret_enc


def test_x25519_adapter_wrong_key() -> None:
    _, pub_bytes = X25519Adapter.generate_keypair()
    other_priv_bytes, _ = X25519Adapter.generate_keypair()
    adapter = X25519Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    shared_secret_dec = adapter.decapsulate(ciphertext, other_priv_bytes)
    assert shared_secret_dec != shared_secret_enc
