"""
Layer: 1
Depends on: quantx_core.interfaces.kem_provider.KEMProvider, quantx_core.types.algorithm_id.AlgorithmId
Implements: MlKem1024Adapter
Outside: KEM combination and HKDF ciphertext/public-key binding (Layer 2 KEMCombiner).
Inside: ML-KEM-1024 key generation, encapsulate, and decapsulate wrapping cryptography (FIPS 203).
Security notes: PQC backend statement: backed by cryptography (pyca) >=48,<51; fail-closed decapsulation on malformed input.
"""

from __future__ import annotations

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import mlkem
from quantx_core.interfaces.kem_provider import KEMProvider
from quantx_core.types.algorithm_id import AlgorithmId


class MlKem1024Adapter(KEMProvider):
    """
    ML-KEM-1024 algorithm adapter wrapping cryptography (pyca) FIPS 203.
    Implements KEMProvider for high-security post-quantum KEM operations.
    """

    algorithm_id: AlgorithmId = AlgorithmId.ML_KEM_1024

    def __init__(self) -> None:
        # Probe backend support at construction
        try:
            _ = mlkem.MLKEM1024PrivateKey
        except AttributeError as exc:
            raise UnsupportedAlgorithm(
                "ML-KEM-1024 is not supported by the underlying cryptography backend"
            ) from exc

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """
        Generates an ML-KEM-1024 keypair. Returns (seed_64_bytes, public_1568_bytes).
        """
        priv = mlkem.MLKEM1024PrivateKey.generate()
        pub = priv.public_key()
        return priv.private_bytes_raw(), pub.public_bytes_raw()

    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulates a shared secret for recipient public key.
        Returns (ciphertext, shared_secret) in Layer-0 order (ciphertext 1,568 B, shared secret 32 B).
        """
        if len(public_key) != 1568:
            raise ValueError(
                f"ML-KEM-1024 public key must be exactly 1,568 bytes, got {len(public_key)}"
            )

        pub = mlkem.MLKEM1024PublicKey.from_public_bytes(public_key)
        shared_secret, ciphertext = pub.encapsulate()
        return ciphertext, shared_secret

    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Decapsulates shared secret. Fails closed returning b"" on malformed input.
        """
        if len(ciphertext) != 1568 or len(private_key) != 64:
            return b""
        try:
            priv = mlkem.MLKEM1024PrivateKey.from_seed_bytes(private_key)
            return priv.decapsulate(ciphertext)
        except Exception:
            return b""
