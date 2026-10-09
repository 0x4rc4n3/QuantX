"""
Layer: 1
Depends on: quantx_crypto_adapters.pqc.ml_dsa_65_adapter.MlDsa65Adapter
Implements: pytest test functions for MlDsa65Adapter
Outside: Testing any other adapter.
Inside: ML-DSA-65 round-trip, exact key/signature sizes, and negative verification tests.
Security notes: PQC backend statement applies: backed by cryptography (pyca) >=48,<51.
"""

from __future__ import annotations

from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter


def test_ml_dsa_65_adapter_sizes_and_roundtrip(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = MlDsa65Adapter.generate_keypair()
    assert len(priv_bytes) == 32
    assert len(pub_bytes) == 1952

    signer = MlDsa65Adapter(private_key=priv_bytes)
    verifier = MlDsa65Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert len(sig) == 3309
    assert verifier.verify(sample_message, sig) is True


def test_ml_dsa_65_adapter_tampered_signature(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = MlDsa65Adapter.generate_keypair()
    signer = MlDsa65Adapter(private_key=priv_bytes)
    verifier = MlDsa65Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    tampered_sig = bytearray(sig)
    tampered_sig[10] ^= 0x55
    assert verifier.verify(sample_message, bytes(tampered_sig)) is False


def test_ml_dsa_65_adapter_wrong_message(sample_message: bytes) -> None:
    priv_bytes, pub_bytes = MlDsa65Adapter.generate_keypair()
    signer = MlDsa65Adapter(private_key=priv_bytes)
    verifier = MlDsa65Adapter(public_key=pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(b"different content", sig) is False


def test_ml_dsa_65_adapter_wrong_key(sample_message: bytes) -> None:
    priv_bytes, _ = MlDsa65Adapter.generate_keypair()
    _, other_pub_bytes = MlDsa65Adapter.generate_keypair()

    signer = MlDsa65Adapter(private_key=priv_bytes)
    verifier = MlDsa65Adapter(public_key=other_pub_bytes)

    sig = signer.sign(sample_message)
    assert verifier.verify(sample_message, sig) is False
