"""
Layer: 2
Depends on: cryptography's HKDF implementation (no in-house KDF, D1)
Implements: derive(shared_secrets, ciphertexts, public_keys) -> bytes — HKDF with ciphertext(s) and public key(s) folded into info
Outside: Wire parsing (kem_wire_format.py); orchestrating which KEMProviders ran (kem_combiner.py).
Inside: The HKDF info-binding construction itself, and only that.
Security notes: Implements SR-7 in full. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

import struct
from typing import Sequence, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from quantx_core.exceptions.malformed_input_error import MalformedInputError

HKDF_DOMAIN: bytes = b"QuantX-KEM-v1\x00"
DERIVED_KEY_LENGTH: int = 32


def build_hkdf_info(
    components: Sequence[Tuple[str, bytes, bytes]],
) -> bytes:
    """
    Construct normative V2 §7 HKDF info:
    b"QuantX-KEM-v1\x00" || u8(component_count) ||
    repeat(component_count times in registry order:
        u16(len(algorithm_id)) || algorithm_id_utf8 ||
        u32(len(public_key)) || public_key ||
        u32(len(ciphertext)) || ciphertext)
    """
    count = len(components)
    if count not in (1, 2):
        raise MalformedInputError(f"HKDF binding expects 1 or 2 components, got {count}")

    info = bytearray()
    info.extend(HKDF_DOMAIN)
    info.append(count)

    for alg_id, pub_key, ct in components:
        alg_bytes = alg_id.encode("utf-8")
        info.extend(struct.pack(">H", len(alg_bytes)))
        info.extend(alg_bytes)
        info.extend(struct.pack(">I", len(pub_key)))
        info.extend(pub_key)
        info.extend(struct.pack(">I", len(ct)))
        info.extend(ct)

    return bytes(info)


def derive(
    shared_secrets: Sequence[bytes],
    components: Sequence[Tuple[str, bytes, bytes]],
) -> bytes:
    """
    Derive the 32-byte shared key using HKDF-SHA256 (SR-7).
    IKM is the concatenation of shared secrets in registry order.
    info is constructed via build_hkdf_info.
    salt=None.
    """
    if len(shared_secrets) != len(components):
        raise MalformedInputError(
            f"Mismatched shared secrets count ({len(shared_secrets)}) and components count ({len(components)})"
        )

    for ss in shared_secrets:
        if not ss:
            raise MalformedInputError("Shared secret must be non-empty")

    ikm = b"".join(shared_secrets)
    info = build_hkdf_info(components)

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=DERIVED_KEY_LENGTH,
        salt=None,
        info=info,
    )
    return hkdf.derive(ikm)
