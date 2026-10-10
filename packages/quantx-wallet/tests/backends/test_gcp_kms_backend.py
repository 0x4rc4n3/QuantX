"""Unit tests for GcpKmsBackend.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.gcp_kms_backend.GcpKmsBackend, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError
Implements: Pytest tests validating Google Cloud KMS custody backend behavior
Outside: Real network Google Cloud infrastructure
Inside: Key generation, resident signing, decapsulation, and non-exportability checks
Security notes: Confirms D-008: resident keys in GCP KMS cannot be exported.
"""

from __future__ import annotations

import pytest
from conftest import MockGcpKmsClient
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_wallet.backends.gcp_kms_backend import GcpKmsBackend
from quantx_wallet.backends.wallet_backend_interface import KeyNotExportableError


def test_gcp_kms_backend_lifecycle() -> None:
    client = MockGcpKmsClient()
    backend = GcpKmsBackend(kms_client=client)

    pub_bytes = backend.generate("gcp-key-1", "ecdsa-p256")
    assert b"BEGIN PUBLIC KEY" in pub_bytes

    signer = backend.signer_for("gcp-key-1")
    sig = signer.sign(b"payload")
    assert sig == b"mock-gcp-kms-signature"

    decapsulator = backend.decapsulator_for("gcp-key-1")
    pt = decapsulator(b"ciphertext")
    assert pt == b"mock-gcp-kms-plaintext"

    # Raw key export is prohibited (D-008)
    with pytest.raises(KeyNotExportableError):
        backend.retrieve("gcp-key-1")


def test_gcp_kms_backend_forced_unavailable_raises() -> None:
    backend = GcpKmsBackend(force_unavailable=True)
    with pytest.raises(BackendUnavailableError):
        backend.generate("k1", "ecdsa-p256")
