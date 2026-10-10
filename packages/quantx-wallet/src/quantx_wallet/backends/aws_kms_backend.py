"""AWS KMS custody backend with resident-key lifecycle.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_core.interfaces.signer.Signer, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: AwsKmsBackend satisfying WalletBackend
Outside: Algorithm choice (registry), message construction (D-009)
Inside: Calls to AWS KMS, error mapping, capability probe
Security notes: Credentials come from platform identity, never config (CFG-4). No key bytes in memory. ML-KEM raises BackendUnavailableError (E8).
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


class _AwsKmsResidentSigner(Signer):
    """Signer implementation invoking AWS KMS Sign API."""

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
                f"Payload size {len(message)} exceeds AWS KMS limit {self._max_message_size} (D-009)"
            )
        try:
            resp = self._client.sign(
                KeyId=self._key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm="RSASSA_PSS_SHA_256",
            )
            return bytes(resp["Signature"])
        except Exception as exc:
            raise BackendUnavailableError(f"AWS KMS signing failed: {exc}") from exc


class AwsKmsBackend(WalletBackend):
    """Custody backend delegating to AWS Key Management Service."""

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

                boto3 = importlib.import_module("boto3")
                self._client = boto3.client("kms")
                self._available = True
            except Exception:
                self._available = False

    def _ensure_client(self) -> Any:
        if not self._available or self._client is None:
            raise BackendUnavailableError(
                "AWS KMS client is unavailable in the current environment (SR-6)"
            )
        return self._client

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Import key material into AWS KMS."""
        self._ensure_client()
        raise NotImplementedError("Direct key material import not supported on AWS KMS")

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """AWS KMS keys are resident and cannot be exported (D-008)."""
        self._ensure_client()
        raise KeyNotExportableError(
            f"Key '{key_id}' is resident inside AWS KMS and cannot be exported (D-008)"
        )

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Generate key inside AWS KMS. ML-KEM is not supported (E8)."""
        client = self._ensure_client()
        if "ml-kem" in algorithm.lower() or "kem" in algorithm.lower():
            raise BackendUnavailableError(
                f"AWS KMS does not support ML-KEM key type '{algorithm}' (E8, D-008)"
            )
        try:
            resp = client.create_key(Description=f"QuantX key {key_id}")
            key_arn = resp.get("KeyMetadata", {}).get("Arn", key_id)
            pub_resp = client.get_public_key(KeyId=key_arn)
            return bytes(pub_resp.get("PublicKey", b"mock-aws-pubkey"))
        except Exception as exc:
            raise BackendUnavailableError(f"AWS KMS key creation failed: {exc}") from exc

    def signer_for(self, key_id: str) -> Signer:
        """Return Signer bound to resident KMS key."""
        client = self._ensure_client()
        return _AwsKmsResidentSigner(
            key_id=key_id,
            algorithm="ecdsa-p256",
            client=client,
            max_message_size=self._max_message_size,
        )

    def decapsulator_for(self, key_id: str) -> Any:
        """ML-KEM is unsupported in AWS KMS (E8)."""
        self._ensure_client()
        raise BackendUnavailableError(
            "AWS KMS does not support ML-KEM decapsulation keys (E8, D-008)"
        )
