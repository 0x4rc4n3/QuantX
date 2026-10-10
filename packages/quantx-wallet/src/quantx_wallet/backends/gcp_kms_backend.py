"""Google Cloud KMS custody backend with resident-key lifecycle.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_core.interfaces.signer.Signer, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: GcpKmsBackend satisfying WalletBackend
Outside: Algorithm choice (registry), message construction (D-009)
Inside: Calls to Google Cloud KMS, error mapping, capability probe
Security notes: Credentials come from platform identity, never config (CFG-4). No key bytes in memory. ML-KEM is preview only (W11).
"""

from __future__ import annotations

from typing import Any

from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.interfaces.signer import Signer

from quantx_wallet.backends.wallet_backend_interface import (
    KeyNotExportableError,
    WalletBackend,
)
from quantx_wallet.vault_metadata import VaultMetadata


class _GcpKmsResidentSigner(Signer):
    """Signer implementation invoking GCP Cloud KMS AsymmetricSign API."""

    def __init__(
        self,
        key_id: str,
        algorithm: str,
        client: Any,
        max_message_size: int,
    ) -> None:
        self._key_id = key_id
        self._algorithm = algorithm
        self._client = client
        self._max_message_size = max_message_size

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def sign(self, message: bytes) -> bytes:
        if len(message) > self._max_message_size:
            raise ValueError(
                f"Payload size {len(message)} exceeds GCP KMS limit {self._max_message_size} (D-009)"
            )
        try:
            resp = self._client.asymmetric_sign(
                name=self._key_id,
                data=message,
            )
            return bytes(resp.signature)
        except Exception as exc:
            raise BackendUnavailableError(f"GCP KMS signing failed: {exc}") from exc


class GcpKmsBackend(WalletBackend):
    """Custody backend delegating to Google Cloud KMS."""

    def __init__(
        self,
        kms_client: Any | None = None,
        max_message_size: int = 4096,
        force_unavailable: bool = False,
    ) -> None:
        self._client = kms_client
        self._max_message_size = max_message_size
        self._force_unavailable = force_unavailable

        if self._force_unavailable:
            self._available = False
        elif self._client is not None:
            self._available = True
        else:
            try:
                import importlib

                kms = importlib.import_module("google.cloud.kms")
                self._client = kms.KeyManagementServiceClient()
                self._available = True
            except Exception:
                self._available = False

    def _ensure_client(self) -> Any:
        if not self._available or self._client is None:
            raise BackendUnavailableError(
                "Google Cloud KMS client is unavailable in current environment (SR-6)"
            )
        return self._client

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Import key material into GCP KMS."""
        self._ensure_client()
        raise NotImplementedError("Direct key material import not supported on GCP KMS")

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """GCP KMS keys are resident and cannot be exported (D-008)."""
        self._ensure_client()
        raise KeyNotExportableError(
            f"Key '{key_id}' is resident inside GCP KMS and cannot be exported (D-008)"
        )

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Generate key inside GCP KMS."""
        client = self._ensure_client()
        try:
            resp = client.create_crypto_key(
                parent="projects/quantx/locations/global/keyRings/default",
                crypto_key_id=key_id,
                crypto_key={"purpose": "ASYMMETRIC_SIGN"},
            )
            pub_key = client.get_public_key(name=f"{resp.name}/cryptoKeyVersions/1")
            return bytes(pub_key.pem.encode("utf-8"))
        except Exception as exc:
            raise BackendUnavailableError(f"GCP KMS key creation failed: {exc}") from exc

    def signer_for(self, key_id: str) -> Signer:
        """Return Signer bound to resident KMS key."""
        client = self._ensure_client()
        return _GcpKmsResidentSigner(
            key_id=key_id,
            algorithm="mldsa65" if "mldsa" in key_id else "ecdsa-p256",
            client=client,
            max_message_size=self._max_message_size,
        )

    def decapsulator_for(self, key_id: str) -> Any:
        """Return decapsulation callable for GCP KMS (preview ML-KEM)."""
        client = self._ensure_client()
        return lambda ciphertext: client.asymmetric_decrypt(
            name=key_id,
            ciphertext=ciphertext,
        ).plaintext
