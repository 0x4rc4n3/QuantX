"""
Layer: 1
Depends on: quantx_crypto_adapters.pqc.ml_kem_1024_adapter.MlKem1024Adapter
Implements: pytest test functions for MlKem1024Adapter
Outside: Testing any other adapter.
Inside: ML-KEM-1024 round-trip, exact sizes, Layer-0 order, and implicit rejection tests.
Security notes: PQC backend statement applies: backed by cryptography (pyca) >=48,<51.
"""

from __future__ import annotations

from quantx_crypto_adapters.pqc.ml_kem_1024_adapter import MlKem1024Adapter


def test_ml_kem_1024_adapter_sizes_and_roundtrip() -> None:
    priv_bytes, pub_bytes = MlKem1024Adapter.generate_keypair()
    assert len(priv_bytes) == 64
    assert len(pub_bytes) == 1568

    adapter = MlKem1024Adapter()
    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    assert len(ciphertext) == 1568
    assert len(shared_secret_enc) == 32

    shared_secret_dec = adapter.decapsulate(ciphertext, priv_bytes)
    assert shared_secret_dec == shared_secret_enc


def test_ml_kem_1024_adapter_implicit_rejection() -> None:
    priv_bytes, pub_bytes = MlKem1024Adapter.generate_keypair()
    adapter = MlKem1024Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    tampered_ct = bytearray(ciphertext)
    tampered_ct[100] ^= 0x01

    shared_secret_dec = adapter.decapsulate(bytes(tampered_ct), priv_bytes)
    assert shared_secret_dec != shared_secret_enc
    assert len(shared_secret_dec) == 32


def test_ml_kem_1024_adapter_wrong_key() -> None:
    _, pub_bytes = MlKem1024Adapter.generate_keypair()
    other_priv_bytes, _ = MlKem1024Adapter.generate_keypair()
    adapter = MlKem1024Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    shared_secret_dec = adapter.decapsulate(ciphertext, other_priv_bytes)
    assert shared_secret_dec != shared_secret_enc
