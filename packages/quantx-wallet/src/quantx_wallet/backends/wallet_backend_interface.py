"""Shared protocol for custody backends.

Layer: 6
Depends on: quantx_core.interfaces.signer.Signer, quantx_wallet.vault_metadata.VaultMetadata
Implements: WalletBackend protocol, KeyNotExportableError, VaultCorruptionError
Outside: Any concrete storage mechanism
Inside: The method shape every backend must satisfy
Security notes: Every implementing backend either really works or raises NotImplementedError/BackendUnavailableError (SR-6). Resident keys raise KeyNotExportableError on retrieve (D-008).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from quantx_core.interfaces.signer import Signer

from quantx_wallet.vault_metadata import VaultMetadata


class KeyNotExportableError(Exception):
    """Raised when an attempt is made to retrieve raw private key bytes from a resident-key backend (D-008)."""


class VaultCorruptionError(Exception):
    """Raised when vault contents or metadata fail authentication or integrity checks (FR-6.3, SR-9)."""


@runtime_checkable
class WalletBackend(Protocol):
    """Protocol satisfied by all KeyWallet custody backends."""

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Store key material and associated authenticated metadata."""
        ...

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """Retrieve key material and associated metadata.

        Raises:
            KeyNotExportableError: If the key is HSM/KMS resident.
            VaultCorruptionError: If file or metadata is corrupt or tampered.
            BackendUnavailableError: If the backend is unreachable.
        """
        ...

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Generate a new keypair within the backend and return the public key bytes."""
        ...

    def signer_for(self, key_id: str) -> Signer:
        """Return a Signer bound to the resident or stored private key."""
        ...

    def decapsulator_for(self, key_id: str) -> Any:
        """Return a decapsulation callable or handle for the resident or stored private key."""
        ...
