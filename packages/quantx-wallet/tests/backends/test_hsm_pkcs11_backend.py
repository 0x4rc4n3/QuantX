"""Unit tests for HsmPkcs11Backend.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.hsm_pkcs11_backend.HsmPkcs11Backend, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError
Implements: Pytest tests validating PKCS#11 HSM resident key lifecycle
Outside: Other backends' mechanics
Inside: Key generation, resident signer delegation, and non-exportability checks
Security notes: Confirms FR-6.5 and D-008: raw private keys cannot be exported from HSM.
"""

from __future__ import annotations

import pytest
from conftest import MockHsmSession
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_wallet.backends.hsm_pkcs11_backend import HsmPkcs11Backend
from quantx_wallet.backends.wallet_backend_interface import KeyNotExportableError


def test_hsm_backend_resident_key_operations() -> None:
    session = MockHsmSession(key_id="hsm-key-1")
    backend = HsmPkcs11Backend(session=session)

    # Key generation produces public key
    pub_bytes = backend.generate("hsm-key-2", "ed25519")
    assert pub_bytes == b"pub-hsm-key-2-ed25519"

    # Resident signer signs payloads
    signer = backend.signer_for("hsm-key-1")
    sig = signer.sign(b"test-message")
    assert sig.startswith(b"sig-for-hsm-key-1")

    # Raw key export is prohibited (D-008)
    with pytest.raises(KeyNotExportableError):
        backend.retrieve("hsm-key-1")


def test_hsm_backend_pqc_unsupported_raises() -> None:
    session = MockHsmSession()
    # Released SoftHSM2 has no PQC support (pqc_supported=False)
    backend = HsmPkcs11Backend(session=session, pqc_supported=False)

    with pytest.raises(BackendUnavailableError):
        backend.generate("pqc-key-1", "ml-dsa-65")


def test_hsm_backend_forced_unavailable_raises() -> None:
    backend = HsmPkcs11Backend(force_unavailable=True)
    with pytest.raises(BackendUnavailableError):
        backend.generate("k1", "ed25519")
