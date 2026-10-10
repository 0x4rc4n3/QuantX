"""Mandatory security test SR-06: Custody backend unavailability raises explicit error.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.hsm_pkcs11_backend.HsmPkcs11Backend, quantx_wallet.backends.os_keychain_backend.OSKeychainBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: SR-06 mandatory test verifying explicit typed error on backend absence
Outside: File-based storage (SR-09)
Inside: Unavailability simulation for OS Keychain and PKCS#11 HSM backends
Security notes: SR-6: Custody backends raise explicit BackendUnavailableError; never silently fallback to memory dict.
"""

from __future__ import annotations

import pytest
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_wallet.backends.hsm_pkcs11_backend import HsmPkcs11Backend
from quantx_wallet.backends.os_keychain_backend import OSKeychainBackend
from quantx_wallet.vault_metadata import VaultMetadata


def test_sr_06_os_keychain_unavailable_raises_explicit_error() -> None:
    # Explicitly unavailable OS keychain backend
    backend = OSKeychainBackend(force_unavailable=True)
    metadata = VaultMetadata(
        key_id="key-1",
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
    )

    with pytest.raises(BackendUnavailableError):
        backend.store("key-1", b"secret-bytes", metadata)

    with pytest.raises(BackendUnavailableError):
        backend.retrieve("key-1")


def test_sr_06_hsm_pkcs11_unavailable_raises_explicit_error() -> None:
    # Explicitly unavailable PKCS#11 HSM backend
    backend = HsmPkcs11Backend(force_unavailable=True)

    with pytest.raises(BackendUnavailableError):
        backend.generate("key-2", "ed25519")

    with pytest.raises(BackendUnavailableError):
        backend.signer_for("key-2")

    with pytest.raises(BackendUnavailableError):
        backend.decapsulator_for("key-2")
