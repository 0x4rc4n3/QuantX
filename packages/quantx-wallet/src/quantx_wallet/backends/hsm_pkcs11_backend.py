"""PKCS#11 HSM key custody backend with resident-key lifecycle.

Layer: 6
Depends on: quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError, quantx_core.interfaces.signer.Signer, quantx_wallet.backends.wallet_backend_interface.KeyNotExportableError, quantx_wallet.backends.wallet_backend_interface.WalletBackend, quantx_wallet.vault_metadata.VaultMetadata
Implements: HsmPkcs11Backend satisfying WalletBackend
Outside: File-based or OS-keychain storage
Inside: PKCS#11 token session handling and resident-key signers
Security notes: SR-6 in full: real integration or explicit typed error; resident keys raise KeyNotExportableError on retrieve (D-008).
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

GATE_REVIEW_REQUIRED: bool = True


class _HsmResidentSigner(Signer):
    """Signer implementation invoking PKCS#11 C_Sign on resident key handles."""

    def __init__(
        self,
        key_id: str,
        algorithm: str,
        session: Any,
        max_payload_size: int,
    ) -> None:
        self._key_id = key_id
        self._algorithm = algorithm
        self._session = session
        self._max_payload_size = max_payload_size

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def sign(self, message: bytes) -> bytes:
        if len(message) > self._max_payload_size:
            raise ValueError(
                f"Payload size {len(message)} exceeds HSM maximum limit {self._max_payload_size} (D-009)"
            )
        try:
            return bytes(self._session.sign(self._key_id, message))
        except Exception as exc:
            raise BackendUnavailableError(f"HSM signing operation failed: {exc}") from exc


class HsmPkcs11Backend(WalletBackend):
    """Custody backend interfacing with PKCS#11 hardware or SoftHSM2."""

    def __init__(
        self,
        module_path: str | None = None,
        pin: str | None = None,
        token_label: str | None = None,
        session: Any | None = None,
        pqc_supported: bool = False,
        max_payload_size: int = 4096,
        force_unavailable: bool = False,
    ) -> None:
        self._module_path = module_path
        self._pin = pin
        self._token_label = token_label
        self._session = session
        self._pqc_supported = pqc_supported
        self._max_payload_size = max_payload_size
        self._force_unavailable = force_unavailable

        if self._force_unavailable:
            self._available = False
        elif self._session is not None:
            self._available = True
        elif self._module_path is not None:
            # Probe PKCS#11 library availability
            try:
                import importlib

                pkcs11 = importlib.import_module("pkcs11")
                lib = pkcs11.lib(self._module_path)
                token = lib.get_token(token_label=self._token_label)
                self._session = token.open(user_pin=self._pin)
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False

    def _ensure_session(self) -> Any:
        if not self._available or self._session is None:
            raise BackendUnavailableError(
                "PKCS#11 HSM module is unreachable or unconfigured (SR-6)"
            )
        return self._session

    def store(
        self,
        key_id: str,
        key_material: bytes,
        metadata: VaultMetadata,
    ) -> None:
        """Import key material into the token."""
        session = self._ensure_session()
        try:
            session.import_key(key_id, key_material, metadata.to_dict())
        except Exception as exc:
            raise BackendUnavailableError(f"Failed to import key into HSM: {exc}") from exc

    def retrieve(self, key_id: str) -> tuple[bytes, VaultMetadata]:
        """HSM keys are resident: raw private keys cannot be extracted (D-008)."""
        self._ensure_session()
        raise KeyNotExportableError(
            f"Key '{key_id}' is resident within the HSM and cannot be exported (D-008)"
        )

    def generate(self, key_id: str, algorithm: str) -> bytes:
        """Generate keypair inside the token and return public key bytes."""
        session = self._ensure_session()
        if (
            "ml-dsa" in algorithm.lower() or "ml-kem" in algorithm.lower()
        ) and not self._pqc_supported:
            raise BackendUnavailableError(
                f"PKCS#11 module does not advertise support for PQC algorithm '{algorithm}' (D-008, SR-6)"
            )
        try:
            pub_bytes = session.generate_keypair(key_id, algorithm)
            return bytes(pub_bytes)
        except Exception as exc:
            raise BackendUnavailableError(f"HSM keypair generation failed: {exc}") from exc

    def signer_for(self, key_id: str) -> Signer:
        """Return a Signer bound to the resident private key handle."""
        session = self._ensure_session()
        algorithm = getattr(session, "get_algorithm", lambda kid: "ed25519")(key_id)
        return _HsmResidentSigner(
            key_id=key_id,
            algorithm=algorithm,
            session=session,
            max_payload_size=self._max_payload_size,
        )

    def decapsulator_for(self, key_id: str) -> Any:
        """Return decapsulation callable bound to the resident KEM handle."""
        session = self._ensure_session()
        return lambda ciphertext: session.decapsulate(key_id, ciphertext)
