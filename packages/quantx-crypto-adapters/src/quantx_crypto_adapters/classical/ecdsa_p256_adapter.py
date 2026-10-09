"""
Layer: 1
Depends on: quantx_core.interfaces.signer.Signer, quantx_core.interfaces.verifier.Verifier, quantx_core.types.algorithm_id.AlgorithmId
Implements: EcdsaP256Adapter
Outside: Algorithm selection and hybrid pairing handled in higher layers.
Inside: ECDSA-P256 key generation, sign, and verify wrapping cryptography.
Security notes: FR-0.1 fail-closed verification; verify() catches exceptions and returns False.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from quantx_core.interfaces.signer import Signer
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.algorithm_id import AlgorithmId


class EcdsaP256Adapter(Signer, Verifier):
    """
    ECDSA-P256 algorithm adapter wrapping cryptography (pyca).
    Implements Signer and Verifier using curve SECP256R1 and SHA-256.
    """

    algorithm_id: AlgorithmId = AlgorithmId.ECDSA_P256

    def __init__(
        self,
        private_key: bytes | None = None,
        public_key: bytes | None = None,
    ) -> None:
        self._private_key: ec.EllipticCurvePrivateKey | None = None
        self._public_key: ec.EllipticCurvePublicKey | None = None

        if private_key is not None:
            loaded_priv = serialization.load_der_private_key(private_key, password=None)
            if not isinstance(loaded_priv, ec.EllipticCurvePrivateKey):
                raise ValueError("Expected an EC private key")
            self._private_key = loaded_priv
            self._public_key = self._private_key.public_key()
        elif public_key is not None:
            loaded_pub = serialization.load_der_public_key(public_key)
            if not isinstance(loaded_pub, ec.EllipticCurvePublicKey):
                raise ValueError("Expected an EC public key")
            self._public_key = loaded_pub

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """
        Generates a fresh ECDSA-P256 keypair.
        Returns (private_pkcs8_der_bytes, public_spki_der_bytes).
        """
        priv = ec.generate_private_key(ec.SECP256R1())
        pub = priv.public_key()
        priv_bytes = priv.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = pub.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return priv_bytes, pub_bytes

    def sign(self, message: bytes) -> bytes:
        """
        Signs message returning DER-encoded ECDSA signature.
        """
        if self._private_key is None:
            raise ValueError("Signer initialized without private key")
        return self._private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verifies ECDSA signature. Catches all errors and returns False (FR-0.1).
        """
        if self._public_key is None:
            return False
        try:
            self._public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
