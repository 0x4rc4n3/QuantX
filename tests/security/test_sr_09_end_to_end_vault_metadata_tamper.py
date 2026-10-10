"""End-to-end security test for SR-9: Vault metadata tampering detected across KeyWallet stack.

Layer: cross-cutting
Depends on: quantx_wallet.key_wallet.KeyWallet, quantx_wallet.backends.encrypted_file_backend.EncryptedFileBackend, quantx_wallet.backends.wallet_backend_interface.VaultCorruptionError
Implements: Mandatory full-stack end-to-end test for SR-9 (vault metadata AAD tampering detection)
Outside: Every other numbered SR item
Inside: Tamper with vault metadata on encrypted file storage and confirm KeyWallet surfaces failure explicitly
Wire format: AES-GCM envelope with AAD-authenticated metadata
Security notes: Mandatory SR-9 end-to-end confirmation spanning quantx-wallet
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.backends.wallet_backend_interface import VaultCorruptionError
from quantx_wallet.key_wallet import KeyWallet


def test_sr_09_end_to_end_vault_metadata_tamper_detected(tmp_path: Path) -> None:
    master_key = b"master_secret_aes256_32bytes_pad"
    canonicalizer = JCSCanonicalizer()

    # 1. Store a key via KeyWallet
    backend = EncryptedFileBackend(
        base_dir=tmp_path, master_key=master_key, canonicalizer=canonicalizer
    )
    wallet = KeyWallet(backend=backend)
    wallet.store(key_id="signing-key-1", key_material=b"super_secret_private_signing_key_32b")

    # 2. Tamper with the unencrypted vault metadata header in the JSON file
    key_file = tmp_path / "signing-key-1.vault"
    content = json.loads(key_file.read_text(encoding="utf-8"))
    assert "metadata" in content
    # Tamper with an authenticated field (rotation_state)
    content["metadata"]["rotation_state"] = "revoked"
    key_file.write_text(json.dumps(content), encoding="utf-8")

    # 3. Reload KeyWallet against tampered vault - AEAD AAD verification must fail
    tampered_backend = EncryptedFileBackend(
        base_dir=tmp_path, master_key=master_key, canonicalizer=canonicalizer
    )
    tampered_wallet = KeyWallet(backend=tampered_backend)

    with pytest.raises(VaultCorruptionError, match="Vault corruption detected"):
        tampered_wallet.retrieve("signing-key-1")
