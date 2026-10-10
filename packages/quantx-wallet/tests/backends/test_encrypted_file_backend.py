"""Unit tests for EncryptedFileBackend non-adversarial path.

Layer: 6
Depends on: quantx_wallet.backends.encrypted_file_backend.EncryptedFileBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: Pytest tests validating genuine store and retrieve round-trips
Outside: Other backends' mechanics
Inside: AES-GCM file round trip validation and metadata persistence
Security notes: Non-adversarial round-trip checks; SR-9 and corruption handling tested separately.
"""

from __future__ import annotations

from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.vault_metadata import VaultMetadata


def test_encrypted_file_backend_roundtrip(
    encrypted_file_backend: EncryptedFileBackend,
) -> None:
    metadata = VaultMetadata(
        key_id="signing-key-1",
        algorithm="ed25519",
        created_at="2026-10-10T12:00:00+00:00",
        rotation_state="active",
        key_format="ed25519-raw-v1",
    )
    secret_bytes = b"0123456789abcdef0123456789abcdef"

    encrypted_file_backend.store("signing-key-1", secret_bytes, metadata)

    retrieved_bytes, retrieved_meta = encrypted_file_backend.retrieve("signing-key-1")
    assert retrieved_bytes == secret_bytes
    assert retrieved_meta.key_id == "signing-key-1"
    assert retrieved_meta.algorithm == "ed25519"
    assert retrieved_meta.rotation_state == "active"
    assert retrieved_meta.key_format == "ed25519-raw-v1"
