"""
Layer: 1
Depends on: quantx_crypto_adapters
Implements: The mandatory automated test for FR-0.1.
Outside: Round-trip success path testing.
Inside: Malformed, truncated, and corrupt inputs against all Layer-1 verify and decapsulate paths.
Security notes: FR-0.1. Verifier.verify() and KEMProvider.decapsulate() fail closed and never raise.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_crypto_adapters.classical.ecdsa_p256_adapter import EcdsaP256Adapter
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_crypto_adapters.pqc.ml_dsa_87_adapter import MlDsa87Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter
from quantx_crypto_adapters.pqc.ml_kem_1024_adapter import MlKem1024Adapter

MALFORMED_INPUTS = [
    b"",
    b"\x00",
    b"\xff" * 7,
    b"truncated",
    b"\x00" * 31,
    b"\x00" * 33,
    b"garbage bytes that do not conform to any expected binary format",
]


@pytest.mark.parametrize(
    "adapter_cls",
    [
        Ed25519Adapter,
        EcdsaP256Adapter,
        MlDsa65Adapter,
        MlDsa87Adapter,
    ],
)
@pytest.mark.parametrize("bad_sig", MALFORMED_INPUTS)
def test_signature_verifiers_fail_closed_on_malformed_signatures(
    adapter_cls: Any,
    bad_sig: bytes,
) -> None:
    _, pub_bytes = adapter_cls.generate_keypair()
    verifier = adapter_cls(public_key=pub_bytes)
    # Must return False and never raise
    assert verifier.verify(b"test message", bad_sig) is False


@pytest.mark.parametrize(
    "kem_cls",
    [
        X25519Adapter,
        MlKem768Adapter,
        MlKem1024Adapter,
    ],
)
@pytest.mark.parametrize("bad_ct", MALFORMED_INPUTS)
def test_kem_providers_fail_closed_on_malformed_ciphertext(
    kem_cls: Any,
    bad_ct: bytes,
) -> None:
    priv_bytes, _ = kem_cls.generate_keypair()
    adapter = kem_cls()
    # Must fail closed (return b"") and never raise
    result = adapter.decapsulate(bad_ct, priv_bytes)
    assert result == b""
