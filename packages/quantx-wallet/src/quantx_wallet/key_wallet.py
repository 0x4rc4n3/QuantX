"""Public KeyWallet facade delegating strictly to injected custody backends.

Layer: 6
Depends on: quantx_core.interfaces.signer.Signer, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: KeyWallet
Outside: Storage mechanics, cryptographic AEAD, hardware communication
Inside: Pure delegation to backend Protocol, parameter validation
Security notes: FR-6.1: contains no storage logic itself; swapping custody backends requires zero changes here.
"""

from __future__ import annotations

from typing import Any

from quantx_core.interfaces.signer import Signer

from quantx_wallet.backends.wallet_backend_interface import WalletBackend
from quantx_wallet.vault_metadata import VaultMetadata


class KeyWallet:
    """Key wallet orchestrator delegating all operations to a WalletBackend."""

    def __init__(self, backend: WalletBackend) -> None:
        self._backend = backend

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata | None = None,
    ) -> None:
        """Store key material and metadata via the injected backend."""
        if not key_id:
            raise ValueError("key_id cannot be empty")
        if metadata is None:
            metadata = VaultMetadata(
                key_id=key_id,
                algorithm="raw",
                created_at="1970-01-01T00:00:00+00:00",
                rotation_state="active",
                key_format="ed25519-raw-v1",
            )
        self._backend.store(key_id, key_material, metadata)

    def retrieve(self, key_id: str) -> bytes:
        """Retrieve raw private key bytes via backend.

        Raises:
            KeyNotExportableError: If key is resident in HSM or KMS.
            VaultCorruptionError: If file or metadata is corrupt or tampered.
            BackendUnavailableError: If backend is unreachable.
        """
        if not key_id:
            raise ValueError("key_id cannot be empty")
        res = self._backend.retrieve(key_id)
        if isinstance(res, tuple):
            return res[0]
        return res

    def retrieve_with_metadata(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """Retrieve both key material and authenticated metadata."""
        if not key_id:
            raise ValueError("key_id cannot be empty")
        return self._backend.retrieve(key_id)

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Generate key inside resident backend and return public key bytes."""
        if not key_id:
            raise ValueError("key_id cannot be empty")
        return self._backend.generate(key_id, algorithm)

    def signer_for(self, key_id: str) -> Signer:
        """Obtain a Signer bound to resident key in backend."""
        if not key_id:
            raise ValueError("key_id cannot be empty")
        return self._backend.signer_for(key_id)

    def decapsulator_for(self, key_id: str) -> Any:
        """Obtain a decapsulator handle from resident backend."""
        if not key_id:
            raise ValueError("key_id cannot be empty")
        return self._backend.decapsulator_for(key_id)
