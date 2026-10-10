"""Unit tests for OSKeychainBackend.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.os_keychain_backend.OSKeychainBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: Pytest tests validating OS keychain store and retrieve round-trips
Outside: Other backends' mechanics
Inside: OS keychain integration with mock/real provider and absence signaling
Security notes: Confirms FR-6.5: works with valid provider or raises explicit error.
"""

from __future__ import annotations

import pytest
from conftest import MockKeyringProvider
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_wallet.backends.os_keychain_backend import OSKeychainBackend
from quantx_wallet.vault_metadata import VaultMetadata


def test_os_keychain_backend_roundtrip_with_provider() -> None:
    provider = MockKeyringProvider()
    backend = OSKeychainBackend(
        service_name="quantx-test",
        keyring_provider=provider,
    )
    metadata = VaultMetadata(
        key_id="keychain-key-1",
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
        rotation_state="active",
        key_format="ed25519-raw-v1",
    )
    secret_bytes = b"keychain-secret-bytes"

    backend.store("keychain-key-1", secret_bytes, metadata)
    retrieved_bytes, retrieved_meta = backend.retrieve("keychain-key-1")

    assert retrieved_bytes == secret_bytes
    assert retrieved_meta.key_id == "keychain-key-1"


def test_os_keychain_backend_forced_unavailable_raises() -> None:
    backend = OSKeychainBackend(force_unavailable=True)
    metadata = VaultMetadata(
        key_id="k1",
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
    )
    with pytest.raises(BackendUnavailableError):
        backend.store("k1", b"secret", metadata)

    with pytest.raises(BackendUnavailableError):
        backend.retrieve("k1")
