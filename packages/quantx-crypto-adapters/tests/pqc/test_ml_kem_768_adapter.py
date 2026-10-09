"""
Layer: 1
Depends on: quantx_crypto_adapters.pqc.ml_kem_768_adapter.MlKem768Adapter
Implements: pytest test functions for MlKem768Adapter
Outside: Testing any other adapter.
Inside: ML-KEM-768 round-trip, exact sizes, Layer-0 order, and implicit rejection tests.
Security notes: PQC backend statement applies: backed by cryptography (pyca) >=48,<51.
"""

from __future__ import annotations

from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter


def test_ml_kem_768_adapter_sizes_and_roundtrip() -> None:
    priv_bytes, pub_bytes = MlKem768Adapter.generate_keypair()
    assert len(priv_bytes) == 64
    assert len(pub_bytes) == 1184

    adapter = MlKem768Adapter()
    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    assert len(ciphertext) == 1088
    assert len(shared_secret_enc) == 32

    shared_secret_dec = adapter.decapsulate(ciphertext, priv_bytes)
    assert shared_secret_dec == shared_secret_enc


def test_ml_kem_768_adapter_implicit_rejection_on_tampered_ciphertext() -> None:
    priv_bytes, pub_bytes = MlKem768Adapter.generate_keypair()
    adapter = MlKem768Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    tampered_ct = bytearray(ciphertext)
    tampered_ct[42] ^= 0x01

    # In FIPS 203 implicit rejection, decapsulate does not raise on altered valid-length ciphertext;
    # it produces a different pseudorandom secret.
    shared_secret_dec = adapter.decapsulate(bytes(tampered_ct), priv_bytes)
    assert shared_secret_dec != shared_secret_enc
    assert len(shared_secret_dec) == 32


def test_ml_kem_768_adapter_wrong_key() -> None:
    _, pub_bytes = MlKem768Adapter.generate_keypair()
    other_priv_bytes, _ = MlKem768Adapter.generate_keypair()
    adapter = MlKem768Adapter()

    ciphertext, shared_secret_enc = adapter.encapsulate(pub_bytes)
    shared_secret_dec = adapter.decapsulate(ciphertext, other_priv_bytes)
    assert shared_secret_dec != shared_secret_enc
