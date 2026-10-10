"""AES-GCM encrypted file key custody backend with AAD-authenticated metadata.

Layer: 6
Depends on: cryptography.hazmat.primitives.ciphers.aead.AESGCM, quantx_core.interfaces.canonicalizer.Canonicalizer, quantx_wallet.backends.wallet_backend_interface.VaultCorruptionError, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: EncryptedFileBackend satisfying WalletBackend
Outside: OS-keychain, HSM, or KMS storage mechanisms
Inside: AES-GCM vault persistence with VaultMetadata authenticated in AAD
Security notes: SR-9 in full: metadata authenticated in AAD; corruption raises explicitly rather than returning empty.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.signer import Signer

from quantx_wallet.backends.wallet_backend_interface import (
    VaultCorruptionError,
    WalletBackend,
)
from quantx_wallet.vault_metadata import VaultMetadata

GATE_REVIEW_REQUIRED: bool = True


class EncryptedFileBackend(WalletBackend):
    """File-backed custody storing AES-GCM encrypted keys with AAD-authenticated metadata."""

    def __init__(
        self,
        base_dir: Path | str,
        master_key: bytes,
        canonicalizer: Canonicalizer,
    ) -> None:
        if len(master_key) != 32:
            raise ValueError(
                f"Master key must be exactly 32 bytes for AES-256-GCM, got {len(master_key)}"
            )
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._master_key = master_key
        self._canonicalizer = canonicalizer
        self._aesgcm = AESGCM(self._master_key)

    def _get_path(self, key_id: str) -> Path:
        return self._base_dir / f"{key_id}.vault"

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Store key material with metadata authenticated in AAD."""
        aad = metadata.to_aad_bytes(self._canonicalizer)
        iv = secrets.token_bytes(12)
        ciphertext = self._aesgcm.encrypt(iv, key_material, aad)

        envelope = {
            "version": 1,
            "metadata": metadata.to_dict(),
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex(),
        }

        path = self._get_path(key_id)
        # Write atomically using a temporary file in the same directory
        temp_path = path.with_suffix(".tmp")
        temp_path.write_bytes(self._canonicalizer.canonicalize(envelope))
        temp_path.replace(path)

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """Retrieve and decrypt key material, verifying metadata in AAD.

        Raises:
            VaultCorruptionError: If file not found, envelope corrupted, or AAD/tag verification fails.
        """
        path = self._get_path(key_id)
        if not path.is_file():
            raise VaultCorruptionError(f"Vault file not found for key '{key_id}'")

        try:
            raw_content = path.read_text(encoding="utf-8")
            data = json.loads(raw_content)
            if not isinstance(data, dict):
                raise ValueError("Envelope is not a JSON object")
            metadata_dict = data["metadata"]
            iv = bytes.fromhex(data["iv"])
            ciphertext = bytes.fromhex(data["ciphertext"])
            metadata = VaultMetadata.from_dict(metadata_dict)
        except Exception as exc:
            raise VaultCorruptionError(f"Vault file for '{key_id}' is corrupted: {exc}") from exc

        aad = metadata.to_aad_bytes(self._canonicalizer)
        try:
            key_material = self._aesgcm.decrypt(iv, ciphertext, aad)
        except InvalidTag as exc:
            raise VaultCorruptionError(
                f"Vault corruption detected for '{key_id}': AEAD authentication failed (tag mismatch or tampered metadata)"
            ) from exc

        return key_material, metadata

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Software file backend does not generate resident keys."""
        raise NotImplementedError("Resident key generation not supported on file backend")

    def signer_for(self, key_id: str) -> Signer:
        """Software file backend does not wrap resident signers."""
        raise NotImplementedError("Resident signers not supported on file backend")

    def decapsulator_for(self, key_id: str) -> Any:
        """Software file backend does not wrap resident decapsulators."""
        raise NotImplementedError("Resident decapsulators not supported on file backend")
