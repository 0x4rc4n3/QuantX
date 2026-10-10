"""Mandatory security test SR-09: Vault metadata included in AEAD AAD.

Layer: 6
Depends on: quantx_wallet.backends.encrypted_file_backend.EncryptedFileBackend, quantx_wallet.backends.wallet_backend_interface.VaultCorruptionError, quantx_wallet.vault_metadata.VaultMetadata
Implements: SR-09 mandatory test verifying metadata tampering detection
Outside: Wholesale ciphertext corruption (tested separately)
Inside: Modifies metadata fields in stored envelope while keeping ciphertext intact
Security notes: SR-09: Tampering with metadata causes AEAD authentication failure and raises VaultCorruptionError.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.backends.wallet_backend_interface import VaultCorruptionError
from quantx_wallet.vault_metadata import VaultMetadata


def test_sr_09_vault_metadata_tampering_detected(
    encrypted_file_backend: EncryptedFileBackend,
    tmp_path: Path,
) -> None:
    key_id = "sr09-key-1"
    metadata = VaultMetadata(
        key_id=key_id,
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
        rotation_state="active",
        key_format="ed25519-raw-v1",
    )
    secret_bytes = b"sr09-secret-payload"

    # Store genuine entry
    encrypted_file_backend.store(key_id, secret_bytes, metadata)

    # Locate vault file on disk
    vault_file = tmp_path / "vault" / f"{key_id}.vault"
    assert vault_file.is_file()

    # Read envelope and tamper ONLY with metadata (e.g. change algorithm or rotation_state)
    envelope = json.loads(vault_file.read_text(encoding="utf-8"))
    envelope["metadata"]["algorithm"] = "ecdsa-p256"  # Tamper with algorithm
    vault_file.write_text(json.dumps(envelope), encoding="utf-8")

    # Attempt retrieve: must fail closed and raise VaultCorruptionError, NEVER return stale/wrong payload
    with pytest.raises(VaultCorruptionError, match="AEAD authentication failed"):
        encrypted_file_backend.retrieve(key_id)


def test_sr_09_rotation_state_tampering_detected(
    encrypted_file_backend: EncryptedFileBackend,
    tmp_path: Path,
) -> None:
    key_id = "sr09-key-2"
    metadata = VaultMetadata(
        key_id=key_id,
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
        rotation_state="active",
        key_format="ed25519-raw-v1",
    )
    secret_bytes = b"sr09-secret-payload-2"

    encrypted_file_backend.store(key_id, secret_bytes, metadata)

    vault_file = tmp_path / "vault" / f"{key_id}.vault"
    envelope = json.loads(vault_file.read_text(encoding="utf-8"))
    envelope["metadata"]["rotation_state"] = "revoked"  # Tamper with rotation state
    vault_file.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(VaultCorruptionError, match="AEAD authentication failed"):
        encrypted_file_backend.retrieve(key_id)
