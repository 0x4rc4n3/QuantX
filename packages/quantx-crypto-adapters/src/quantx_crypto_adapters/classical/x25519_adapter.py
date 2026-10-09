"""
Layer: 1
Depends on: quantx_core.interfaces.kem_provider.KEMProvider, quantx_core.types.algorithm_id.AlgorithmId
Implements: X25519Adapter
Outside: KEM combination and HKDF ciphertext/public-key binding (Layer 2 KEMCombiner).
Inside: X25519 key generation, ephemeral encapsulation, and decapsulation wrapping cryptography.
Security notes: D-015 ephemeral key KEM mapping; fail-closed decapsulation returns empty bytes on malformed input.
"""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import x25519
from quantx_core.interfaces.kem_provider import KEMProvider
from quantx_core.types.algorithm_id import AlgorithmId


class X25519Adapter(KEMProvider):
    """
    X25519 KEM adapter wrapping Diffie-Hellman key exchange as a KEM (D-015).
    Ephemeral keypair generated per encapsulate call; decapsulate fails closed.
    """

    algorithm_id: AlgorithmId = AlgorithmId.X25519

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """
        Generates an X25519 keypair. Returns (private_bytes_raw, public_bytes_raw).
        """
        priv = x25519.X25519PrivateKey.generate()
        pub = priv.public_key()
        return priv.private_bytes_raw(), pub.public_bytes_raw()

    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulates a shared secret for recipient public key.
        Returns (ciphertext, shared_secret) where ciphertext is ephemeral public key.
        """
        if len(public_key) != 32:
            raise ValueError(f"X25519 public key must be exactly 32 bytes, got {len(public_key)}")

        recipient_pub = x25519.X25519PublicKey.from_public_bytes(public_key)
        ephemeral_priv = x25519.X25519PrivateKey.generate()
        ciphertext = ephemeral_priv.public_key().public_bytes_raw()
        shared_secret = ephemeral_priv.exchange(recipient_pub)

        if shared_secret == b"\x00" * 32:
            raise ValueError("All-zero Diffie-Hellman output rejected (D-015)")

        return ciphertext, shared_secret

    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Decapsulates shared secret. Fails closed on any malformed input, returning b"".
        """
        if len(ciphertext) != 32 or len(private_key) != 32:
            return b""
        try:
            priv = x25519.X25519PrivateKey.from_private_bytes(private_key)
            ephemeral_pub = x25519.X25519PublicKey.from_public_bytes(ciphertext)
            shared_secret = priv.exchange(ephemeral_pub)
            if shared_secret == b"\x00" * 32:
                return b""
            return shared_secret
        except Exception:
            return b""
