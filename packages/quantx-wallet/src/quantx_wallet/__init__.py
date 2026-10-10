"""QuantX wallet package for key custody and recovery.

Layer: 6
Depends on: quantx_wallet.backends, quantx_wallet.backup_code_manager, quantx_wallet.device_linker, quantx_wallet.key_wallet, quantx_wallet.vault_metadata
Implements: Package exports for key custody, backends, and recovery
Outside: Higher layer orchestration and REST interfaces
Inside: Facades and value types for wallet storage, recovery, and pairing
Security notes: Resident keys never exported; AEAD AAD integrity enforcement; single-use recovery credentials.
"""

from __future__ import annotations

from quantx_wallet.backends.aws_kms_backend import AwsKmsBackend
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.backends.gcp_kms_backend import GcpKmsBackend
from quantx_wallet.backends.hsm_pkcs11_backend import HsmPkcs11Backend
from quantx_wallet.backends.os_keychain_backend import OSKeychainBackend
from quantx_wallet.backends.wallet_backend_interface import (
    KeyNotExportableError,
    VaultCorruptionError,
    WalletBackend,
)
from quantx_wallet.backup_code_manager import BackupCodeManager
from quantx_wallet.device_linker import DeviceLinker
from quantx_wallet.key_wallet import KeyWallet
from quantx_wallet.vault_metadata import VaultMetadata

__all__ = [
    "AwsKmsBackend",
    "BackupCodeManager",
    "DeviceLinker",
    "EncryptedFileBackend",
    "GcpKmsBackend",
    "HsmPkcs11Backend",
    "KeyNotExportableError",
    "KeyWallet",
    "OSKeychainBackend",
    "VaultCorruptionError",
    "VaultMetadata",
    "WalletBackend",
]
