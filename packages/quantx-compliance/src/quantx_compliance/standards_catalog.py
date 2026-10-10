"""Static reference catalog mapping cryptographic algorithms to standards references.

Layer: 10
Depends on: quantx_core.types.algorithm_id.AlgorithmId, quantx_compliance.crypto_bom_model.CryptoBOMFinding
Implements: StandardsCatalog with static standards reference lookups
Outside: Scanning for algorithms in the first place (scanners/); report formatting (compliance_report_generator.py)
Inside: Static reference data mapping algorithms to regulatory and standards bodies (NIST, FIPS, RFC, ANSI)
Wire format: Static lookup table / StandardReference dataclasses
Security notes: None - this is reference data, not a security-enforcing component
"""

from __future__ import annotations

from dataclasses import dataclass

from quantx_core.types.algorithm_id import AlgorithmId

from quantx_compliance.crypto_bom_model import CryptoBOMFinding


@dataclass(frozen=True)
class StandardReference:
    """Reference to a cryptographic standard or regulatory specification."""

    standard_id: str
    title: str
    status: str  # e.g., 'Standard', 'Approved', 'Legacy', 'Deprecated'
    notes: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "standard_id": self.standard_id,
            "title": self.title,
            "status": self.status,
            "notes": self.notes,
        }


# Known standards definitions
FIPS_203 = StandardReference(
    standard_id="FIPS-203",
    title="Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)",
    status="Standard",
    notes="NIST post-quantum cryptographic standard for key establishment.",
)

FIPS_204 = StandardReference(
    standard_id="FIPS-204",
    title="Module-Lattice-Based Digital Signature Standard (ML-DSA)",
    status="Standard",
    notes="NIST post-quantum cryptographic standard for digital signatures.",
)

FIPS_205 = StandardReference(
    standard_id="FIPS-205",
    title="Stateless Hash-Based Digital Signature Standard (SLH-DSA)",
    status="Standard",
    notes="NIST post-quantum cryptographic standard for stateless hash-based signatures.",
)

RFC_7748 = StandardReference(
    standard_id="RFC-7748",
    title="Elliptic Curves for Security (Curve25519 / X25519)",
    status="Standard",
    notes="IETF specification for high-speed Diffie-Hellman on Curve25519.",
)

RFC_8032 = StandardReference(
    standard_id="RFC-8032",
    title="Edwards-Curve Digital Signature Algorithm (EdDSA / Ed25519)",
    status="Standard",
    notes="IETF specification for Ed25519 signature scheme.",
)

FIPS_186_5 = StandardReference(
    standard_id="FIPS-186-5",
    title="Digital Signature Standard (DSS)",
    status="Standard",
    notes="NIST specification for ECDSA, RSA, and EdDSA signature algorithms.",
)

NIST_SP_800_56A = StandardReference(
    standard_id="NIST-SP-800-56A",
    title="Recommendation for Pair-Wise Key-Establishment Schemes Using Discrete Logarithm Cryptography",
    status="Approved",
    notes="NIST guidance for key establishment using ECDH and DH.",
)

FIPS_197 = StandardReference(
    standard_id="FIPS-197",
    title="Advanced Encryption Standard (AES)",
    status="Standard",
    notes="NIST symmetric block cipher specification.",
)

NIST_SP_800_38D = StandardReference(
    standard_id="NIST-SP-800-38D",
    title="Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM)",
    status="Approved",
    notes="NIST authenticated encryption mode for block ciphers.",
)

FIPS_180_4 = StandardReference(
    standard_id="FIPS-180-4",
    title="Secure Hash Standard (SHS)",
    status="Standard",
    notes="NIST specification for SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512.",
)

RFC_8446 = StandardReference(
    standard_id="RFC-8446",
    title="The Transport Layer Security (TLS) Protocol Version 1.3",
    status="Standard",
    notes="IETF specification for TLS 1.3.",
)

RFC_5246 = StandardReference(
    standard_id="RFC-5246",
    title="The Transport Layer Security (TLS) Protocol Version 1.2",
    status="Legacy",
    notes="IETF specification for TLS 1.2.",
)

IETF_HYBRID_TLS = StandardReference(
    standard_id="IETF-HYBRID-TLS",
    title="Post-quantum Hybrid Key Exchange in TLS 1.3",
    status="Draft",
    notes="IETF working group draft for hybrid classical + post-quantum key exchange (e.g. X25519MLKEM768).",
)


_ALGORITHM_STANDARDS_MAP: dict[str, list[StandardReference]] = {
    "ml-kem-768": [FIPS_203],
    "ml-kem-1024": [FIPS_203],
    "mlkem768": [FIPS_203],
    "mlkem1024": [FIPS_203],
    "ml-dsa-65": [FIPS_204],
    "ml-dsa-87": [FIPS_204],
    "mldsa65": [FIPS_204],
    "mldsa87": [FIPS_204],
    "slh-dsa": [FIPS_205],
    "x25519": [RFC_7748, NIST_SP_800_56A],
    "ed25519": [RFC_8032, FIPS_186_5],
    "ecdsa-p256": [FIPS_186_5, NIST_SP_800_56A],
    "ecdsa_p256": [FIPS_186_5, NIST_SP_800_56A],
    "p256": [FIPS_186_5, NIST_SP_800_56A],
    "secp256r1": [FIPS_186_5, NIST_SP_800_56A],
    "rsa-2048": [FIPS_186_5],
    "rsa-4096": [FIPS_186_5],
    "rsa": [FIPS_186_5],
    "aes-256-gcm": [FIPS_197, NIST_SP_800_38D],
    "aes-128-gcm": [FIPS_197, NIST_SP_800_38D],
    "aes": [FIPS_197],
    "sha-256": [FIPS_180_4],
    "sha-512": [FIPS_180_4],
    "sha256": [FIPS_180_4],
    "sha512": [FIPS_180_4],
    "tls1.3": [RFC_8446],
    "tls1.2": [RFC_5246],
    "x25519mlkem768": [IETF_HYBRID_TLS, FIPS_203, RFC_7748],
}


class StandardsCatalog:
    """Static catalog mapping algorithm identifiers and findings to standards references."""

    def __init__(self, mapping: dict[str, list[StandardReference]] | None = None) -> None:
        self._mapping = dict(_ALGORITHM_STANDARDS_MAP if mapping is None else mapping)
        self._all_standards: set[str] = {
            ref.standard_id for refs in self._mapping.values() for ref in refs
        }

    def _normalize_key(self, alg: AlgorithmId | str | CryptoBOMFinding) -> str:
        if isinstance(alg, CryptoBOMFinding):
            target = alg.algorithm
        else:
            target = alg

        raw = target.value if isinstance(target, AlgorithmId) else str(target)
        return raw.strip().lower().replace("_", "-")

    def lookup(
        self, algorithm_or_finding: AlgorithmId | str | CryptoBOMFinding
    ) -> list[StandardReference]:
        """Look up all standard references associated with an algorithm or finding."""
        key = self._normalize_key(algorithm_or_finding)
        # Check direct match
        if key in self._mapping:
            return list(self._mapping[key])

        # Try key without hyphens
        no_hyphen = key.replace("-", "")
        if no_hyphen in self._mapping:
            return list(self._mapping[no_hyphen])

        # Partial matching for common patterns (e.g. rsa2048, ecdsa, aes)
        for pattern, refs in self._mapping.items():
            if pattern in key or key in pattern:
                return list(refs)

        return []

    def has_standard(self, standard_id: str) -> bool:
        """Check if a standard ID is registered in this catalog."""
        return standard_id.upper() in {s.upper() for s in self._all_standards}

    def get_supported_standards(self) -> set[str]:
        """Return all unique standard IDs present in this catalog."""
        return set(self._all_standards)
