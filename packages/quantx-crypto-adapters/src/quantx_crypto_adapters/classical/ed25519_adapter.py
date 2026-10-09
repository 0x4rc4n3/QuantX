"""
Layer: 1
Depends on: quantx_core.interfaces.signer.Signer, quantx_core.interfaces.verifier.Verifier, quantx_core.types.algorithm_id.AlgorithmId
Implements: Ed25519Adapter
Outside: Branching on algorithm family; handled in AlgorithmRegistry.
Inside: Ed25519 key generation, sign, and verify wrapping cryptography.
Security notes: FR-0.1 fail-closed verification; verify() never raises.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from quantx_core.interfaces.signer import Signer
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.algorithm_id import AlgorithmId


class Ed25519Adapter(Signer, Verifier):
    """
    Ed25519 algorithm adapter wrapping cryptography (pyca).
    Implements Signer and Verifier for the classical leg of hybrid signatures.
    """

    algorithm_id: AlgorithmId = AlgorithmId.ED25519

    def __init__(
        self,
        private_key: bytes | None = None,
        public_key: bytes | None = None,
    ) -> None:
        self._private_key: ed25519.Ed25519PrivateKey | None = None
        self._public_key: ed25519.Ed25519PublicKey | None = None

        if private_key is not None:
            self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
            self._public_key = self._private_key.public_key()
        elif public_key is not None:
            self._public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """
        Generates a fresh Ed25519 keypair. Returns (private_bytes_raw, public_bytes_raw).
        """
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        return priv.private_bytes_raw(), pub.public_bytes_raw()

    def sign(self, message: bytes) -> bytes:
        """
        Signs message returning 64-byte Ed25519 signature.
        """
        if self._private_key is None:
            raise ValueError("Signer initialized without private key")
        return self._private_key.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verifies Ed25519 signature. Catches all errors and returns False (FR-0.1).
        """
        if self._public_key is None:
            return False
        try:
            self._public_key.verify(signature, message)
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
