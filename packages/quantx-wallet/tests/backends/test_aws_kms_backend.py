"""Unit tests for AwsKmsBackend.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.aws_kms_backend.AwsKmsBackend, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError
Implements: Pytest tests validating AWS KMS custody backend behavior
Outside: Real network AWS infrastructure
Inside: Key generation, ML-KEM rejection (E8), resident signing, and non-exportability checks
Security notes: Confirms D-008 and E8: AWS KMS rejects ML-KEM and prevents private key export.
"""

from __future__ import annotations

import pytest
from conftest import MockAwsKmsClient
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_wallet.backends.aws_kms_backend import AwsKmsBackend
from quantx_wallet.backends.wallet_backend_interface import KeyNotExportableError


def test_aws_kms_backend_lifecycle() -> None:
    client = MockAwsKmsClient()
    backend = AwsKmsBackend(kms_client=client)

    pub_bytes = backend.generate("aws-key-1", "ecdsa-p256")
    assert pub_bytes == b"mock-aws-kms-public-key"

    signer = backend.signer_for("aws-key-1")
    sig = signer.sign(b"payload")
    assert sig == b"mock-aws-kms-signature"

    # Raw key export is prohibited (D-008)
    with pytest.raises(KeyNotExportableError):
        backend.retrieve("aws-key-1")


def test_aws_kms_backend_rejects_ml_kem_e8() -> None:
    client = MockAwsKmsClient()
    backend = AwsKmsBackend(kms_client=client)

    # AWS KMS has no ML-KEM key type (E8)
    with pytest.raises(BackendUnavailableError):
        backend.generate("kem-key-1", "ml-kem-768")

    with pytest.raises(BackendUnavailableError):
        backend.decapsulator_for("kem-key-1")


def test_aws_kms_backend_forced_unavailable_raises() -> None:
    backend = AwsKmsBackend(force_unavailable=True)
    with pytest.raises(BackendUnavailableError):
        backend.generate("k1", "ecdsa-p256")
