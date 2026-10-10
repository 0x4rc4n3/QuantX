"""Mandatory test FR-6.3: Corrupted vault file raises explicit error, never silent empty.

Layer: 6
Depends on: quantx_wallet.backends.encrypted_file_backend.EncryptedFileBackend, quantx_wallet.backends.wallet_backend_interface.VaultCorruptionError, quantx_wallet.vault_metadata.VaultMetadata
Implements: FR-6.3 mandatory test verifying explicit error on vault corruption
Outside: Metadata-only tampering (covered by SR-09)
Inside: Wholesale byte corruption, invalid JSON, and truncated file handling
Security notes: FR-6.3: Corruption of vault contents raises VaultCorruptionError; never silently returns empty.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.backends.wallet_backend_interface import VaultCorruptionError
from quantx_wallet.vault_metadata import VaultMetadata


def test_vault_wholesale_byte_corruption_raises(
    encrypted_file_backend: EncryptedFileBackend,
    tmp_path: Path,
) -> None:
    key_id = "corrupt-key-1"
    metadata = VaultMetadata(
        key_id=key_id,
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
    )
    encrypted_file_backend.store(key_id, b"sensitive-data", metadata)

    vault_file = tmp_path / "vault" / f"{key_id}.vault"
    # Overwrite file with garbage bytes
    vault_file.write_bytes(b"\x00\xff\xee\xdd\x00GARBAGE_BYTES_CORRUPTED\x00")

    with pytest.raises(VaultCorruptionError):
        encrypted_file_backend.retrieve(key_id)


def test_vault_nonexistent_file_raises(
    encrypted_file_backend: EncryptedFileBackend,
) -> None:
    with pytest.raises(VaultCorruptionError, match="Vault file not found"):
        encrypted_file_backend.retrieve("nonexistent-key")


def test_vault_truncated_empty_file_raises(
    encrypted_file_backend: EncryptedFileBackend,
    tmp_path: Path,
) -> None:
    key_id = "corrupt-key-2"
    vault_file = tmp_path / "vault" / f"{key_id}.vault"
    vault_file.write_bytes(b"")

    with pytest.raises(VaultCorruptionError):
        encrypted_file_backend.retrieve(key_id)
