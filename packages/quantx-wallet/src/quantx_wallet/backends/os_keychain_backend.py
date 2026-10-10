"""OS Keychain key custody backend.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: OSKeychainBackend satisfying WalletBackend
Outside: File-based, HSM-based, or KMS-based storage
Inside: Host OS keychain integration with explicit error signaling on absence
Security notes: SR-6 in full: real integration or explicit typed error, never a silent in-memory-dict fallback.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.signer import Signer

from quantx_wallet.backends.wallet_backend_interface import (
    VaultCorruptionError,
    WalletBackend,
)
from quantx_wallet.vault_metadata import VaultMetadata

GATE_REVIEW_REQUIRED: bool = True


class OSKeychainBackend(WalletBackend):
    """Custody backend delegating to OS Keychain / Secret Service API."""

    def __init__(
        self,
        service_name: str = "quantx",
        keyring_provider: Any | None = None,
        force_unavailable: bool = False,
        canonicalizer: Canonicalizer | None = None,
    ) -> None:
        self._service_name = service_name
        self._force_unavailable = force_unavailable
        self._provider = keyring_provider
        self._canonicalizer: Canonicalizer = canonicalizer or JCSCanonicalizer()

        if self._force_unavailable:
            self._available = False
        elif self._provider is not None:
            self._available = True
        else:
            # Probe system keyring availability
            try:
                import importlib

                keyring = importlib.import_module("keyring")
                # Check if default keyring is actually functional and not a fail/null backend
                backend_priority = getattr(keyring.get_keyring(), "priority", 0)
                if backend_priority > 0:
                    self._provider = keyring
                    self._available = True
                else:
                    self._available = False
            except Exception:
                self._available = False

    def _ensure_provider(self) -> Any:
        if not self._available or self._provider is None:
            raise BackendUnavailableError(
                "OS keychain service is not available in the current environment"
            )
        return self._provider

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Store key material and serialized metadata into the OS keychain."""
        provider = self._ensure_provider()
        payload = {
            "key_material_b64": base64.b64encode(key_material).decode("ascii"),
            "metadata": metadata.to_dict(),
        }
        payload_str = self._canonicalizer.canonicalize(payload).decode("utf-8")
        try:
            provider.set_password(
                self._service_name,
                key_id,
                payload_str,
            )
        except Exception as exc:
            raise BackendUnavailableError(
                f"Failed to store key '{key_id}' in OS keychain: {exc}"
            ) from exc

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """Retrieve key material and metadata from the OS keychain."""
        provider = self._ensure_provider()
        try:
            raw = provider.get_password(self._service_name, key_id)
        except Exception as exc:
            raise BackendUnavailableError(
                f"Failed to retrieve key '{key_id}' from OS keychain: {exc}"
            ) from exc

        if raw is None:
            raise VaultCorruptionError(f"Key '{key_id}' not found in OS keychain service")

        try:
            data = json.loads(raw)
            key_material = base64.b64decode(data["key_material_b64"])
            metadata = VaultMetadata.from_dict(data["metadata"])
            return key_material, metadata
        except Exception as exc:
            raise VaultCorruptionError(
                f"Malformed payload in OS keychain for key '{key_id}': {exc}"
            ) from exc

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """OS keychain stores raw software keys; does not generate on-token resident keys."""
        raise NotImplementedError("Resident key generation not supported on OS keychain")

    def signer_for(self, key_id: str) -> Signer:
        """OS keychain does not wrap resident signers."""
        raise NotImplementedError("Resident signers not supported on OS keychain")

    def decapsulator_for(self, key_id: str) -> Any:
        """OS keychain does not wrap resident decapsulators."""
        raise NotImplementedError("Resident decapsulators not supported on OS keychain")
