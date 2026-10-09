"""
Layer: 1
Depends on: quantx_core.interfaces.signer.Signer, quantx_core.interfaces.verifier.Verifier, quantx_core.types.algorithm_id.AlgorithmId
Implements: MlDsa65Adapter
Outside: Combining with classical Ed25519; managed in Layer 2 SignatureCombiner.
Inside: ML-DSA-65 key generation, sign, and verify wrapping cryptography (FIPS 204).
Security notes: PQC backend statement: backed by cryptography (pyca) >=48,<51; FR-0.1 fail-closed verification.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import mldsa
from quantx_core.interfaces.signer import Signer
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.algorithm_id import AlgorithmId


class MlDsa65Adapter(Signer, Verifier):
    """
    ML-DSA-65 algorithm adapter wrapping cryptography (pyca) FIPS 204.
    Implements Signer and Verifier for the PQC leg of hybrid signatures.
    """

    algorithm_id: AlgorithmId = AlgorithmId.ML_DSA_65

    def __init__(
        self,
        private_key: bytes | None = None,
        public_key: bytes | None = None,
    ) -> None:
        # Probe backend support at construction
        try:
            _ = mldsa.MLDSA65PrivateKey
        except AttributeError as exc:
            raise UnsupportedAlgorithm(
                "ML-DSA-65 is not supported by the underlying cryptography backend"
            ) from exc

        self._private_key: mldsa.MLDSA65PrivateKey | None = None
        self._public_key: mldsa.MLDSA65PublicKey | None = None

        if private_key is not None:
            self._private_key = mldsa.MLDSA65PrivateKey.from_seed_bytes(private_key)
            self._public_key = self._private_key.public_key()
        elif public_key is not None:
            try:
                self._public_key = mldsa.MLDSA65PublicKey.from_public_bytes(public_key)
            except Exception:
                # Retain None so verify() returns False cleanly
                self._public_key = None

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """
        Generates an ML-DSA-65 keypair. Returns (seed_32_bytes, public_1952_bytes).
        """
        priv = mldsa.MLDSA65PrivateKey.generate()
        pub = priv.public_key()
        return priv.private_bytes_raw(), pub.public_bytes_raw()

    def sign(self, message: bytes) -> bytes:
        """
        Signs message returning 3,309-byte ML-DSA-65 signature with context=None.
        """
        if self._private_key is None:
            raise ValueError("Signer initialized without private key")
        return self._private_key.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verifies ML-DSA-65 signature. Catches all errors and returns False (FR-0.1).
        """
        if self._public_key is None:
            return False
        try:
            self._public_key.verify(signature, message)
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
