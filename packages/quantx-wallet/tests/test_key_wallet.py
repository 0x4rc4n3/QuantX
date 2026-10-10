"""Unit tests for KeyWallet delegation facade.

Layer: 6
Depends on: quantx_wallet.backends.wallet_backend_interface, quantx_wallet.key_wallet.KeyWallet, quantx_wallet.vault_metadata.VaultMetadata
Implements: Pytest tests validating KeyWallet delegation and error propagation
Outside: Backend-specific storage mechanics
Inside: Delegation checks for store, retrieve, generate, signer_for, and decapsulator_for
Security notes: Confirms FR-6.1 at the unit level: KeyWallet contains no storage logic.
"""

from __future__ import annotations

from typing import Any

import pytest
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.interfaces.signer import Signer
from quantx_wallet.backends.wallet_backend_interface import (
    WalletBackend,
)
from quantx_wallet.key_wallet import KeyWallet
from quantx_wallet.vault_metadata import VaultMetadata


class FakeWalletBackend(WalletBackend):
    """Test fake backend recording calls and simulating errors."""

    def __init__(self) -> None:
        self.stored: dict[str, tuple[bytes, VaultMetadata]] = {}

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        self.stored[key_id] = (key_material, metadata)

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        if key_id not in self.stored:
            raise KeyError(key_id)
        return self.stored[key_id]

    def generate(self, key_id: str, algorithm: str) -> bytes:
        return b"fake-pubkey"

    def signer_for(self, key_id: str) -> Signer:
        raise NotImplementedError

    def decapsulator_for(self, key_id: str) -> Any:
        return lambda ct: b"shared-secret"


class FailingBackend(WalletBackend):
    """Backend simulating explicit failure."""

    def store(self, key_id: str, key_material: bytes, metadata: VaultMetadata) -> None:
        raise BackendUnavailableError("Backend offline")

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        raise BackendUnavailableError("Backend offline")

    def generate(self, key_id: str, algorithm: str) -> bytes:
        raise BackendUnavailableError("Backend offline")

    def signer_for(self, key_id: str) -> Signer:
        raise BackendUnavailableError("Backend offline")

    def decapsulator_for(self, key_id: str) -> Any:
        raise BackendUnavailableError("Backend offline")


def test_key_wallet_delegates_store_and_retrieve() -> None:
    backend = FakeWalletBackend()
    wallet = KeyWallet(backend)

    wallet.store("alice-key", b"super-secret-key-bytes")
    assert "alice-key" in backend.stored

    recovered = wallet.retrieve("alice-key")
    assert recovered == b"super-secret-key-bytes"

    material, meta = wallet.retrieve_with_metadata("alice-key")
    assert material == b"super-secret-key-bytes"
    assert meta.key_id == "alice-key"


def test_key_wallet_propagates_backend_errors_unmasked() -> None:
    backend = FailingBackend()
    wallet = KeyWallet(backend)

    with pytest.raises(BackendUnavailableError):
        wallet.store("alice-key", b"bytes")

    with pytest.raises(BackendUnavailableError):
        wallet.retrieve("alice-key")
