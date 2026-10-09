"""
Layer: 1
Depends on: quantx_crypto_adapters
Implements: pytest fixtures for quantx-crypto-adapters tests
Outside: Test assertions themselves.
Inside: Fixture construction for keypairs and sample messages.
Security notes: Foundation testing rules in 10-security-requirements.md.
"""

from __future__ import annotations

import pytest
from quantx_crypto_adapters.classical.ecdsa_p256_adapter import EcdsaP256Adapter
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_crypto_adapters.pqc.ml_dsa_87_adapter import MlDsa87Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter
from quantx_crypto_adapters.pqc.ml_kem_1024_adapter import MlKem1024Adapter


@pytest.fixture
def sample_message() -> bytes:
    return b"QuantX cryptographic adapter test message 2026"


@pytest.fixture
def ed25519_keypair() -> tuple[bytes, bytes]:
    return Ed25519Adapter.generate_keypair()


@pytest.fixture
def ecdsa_p256_keypair() -> tuple[bytes, bytes]:
    return EcdsaP256Adapter.generate_keypair()


@pytest.fixture
def x25519_keypair() -> tuple[bytes, bytes]:
    return X25519Adapter.generate_keypair()


@pytest.fixture
def ml_dsa_65_keypair() -> tuple[bytes, bytes]:
    return MlDsa65Adapter.generate_keypair()


@pytest.fixture
def ml_dsa_87_keypair() -> tuple[bytes, bytes]:
    return MlDsa87Adapter.generate_keypair()


@pytest.fixture
def ml_kem_768_keypair() -> tuple[bytes, bytes]:
    return MlKem768Adapter.generate_keypair()


@pytest.fixture
def ml_kem_1024_keypair() -> tuple[bytes, bytes]:
    return MlKem1024Adapter.generate_keypair()
