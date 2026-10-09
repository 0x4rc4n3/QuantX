"""
Layer: 0
Depends on: None
Implements: AlgorithmId
Outside: Algorithm adapter registration and role composition in AlgorithmRegistry (Layer 3).
Inside: Value type enum identifying concrete cryptographic algorithms.
Security notes: P2 (one algorithm per adapter file). SLH_DSA is reserved but blocked upstream (D-006); registry fails closed on unregistered algorithms.
"""

from __future__ import annotations

from enum import Enum


class AlgorithmId(str, Enum):
    """
    Identifies concrete cryptographic algorithms supported or reserved by QuantX.
    """

    ED25519 = "ed25519"
    ECDSA_P256 = "ecdsa-p256"
    ML_DSA_65 = "ml-dsa-65"
    ML_DSA_87 = "ml-dsa-87"
    SLH_DSA = "slh-dsa"  # Reserved upstream (D-006)
    X25519 = "x25519"
    ML_KEM_768 = "ml-kem-768"
    ML_KEM_1024 = "ml-kem-1024"

    def __str__(self) -> str:
        return self.value
