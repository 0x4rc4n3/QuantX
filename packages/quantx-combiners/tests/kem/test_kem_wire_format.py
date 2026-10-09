"""
Layer: 2
Depends on: kem_wire_format.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies deterministic parsing, round-trip encoding, and bounds checking.
"""

from __future__ import annotations

import pytest
from quantx_combiners.kem import kem_wire_format
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode


def test_classical_kem_container_smoke_vector() -> None:
    """
    Test normative smoke vector from V2 §11:
    010301000678323535313900000002aabb00000003010203
    Decode as version 1, CLASSICAL_ONLY, one x25519 component with public key aabb and ciphertext 010203.
    """
    raw_hex = "010301000678323535313900000002aabb00000003010203"
    wire_bytes = bytes.fromhex(raw_hex)

    mode, components = kem_wire_format.decode(wire_bytes)
    assert mode == Mode.CLASSICAL_ONLY
    assert len(components) == 1
    alg, pubkey, ct = components[0]
    assert alg == "x25519"
    assert pubkey == bytes.fromhex("aabb")
    assert ct == bytes.fromhex("010203")

    # Round trip
    encoded = kem_wire_format.encode(mode, components)
    assert encoded == wire_bytes


def test_kem_wire_format_roundtrip_all_modes() -> None:
    # 1. HYBRID
    hybrid_comps = [
        ("x25519", b"pub1" * 8, b"ct1" * 8),
        ("ml-kem-768", b"pub2" * 50, b"ct2" * 50),
    ]
    encoded_hybrid = kem_wire_format.encode(Mode.HYBRID, hybrid_comps)
    dec_mode, dec_comps = kem_wire_format.decode(encoded_hybrid)
    assert dec_mode == Mode.HYBRID
    assert dec_comps == tuple(hybrid_comps)

    # 2. PQC_ONLY
    pqc_comps = [("ml-kem-768", b"pub_pqc" * 50, b"ct_pqc" * 50)]
    encoded_pqc = kem_wire_format.encode(Mode.PQC_ONLY, pqc_comps)
    dec_mode, dec_comps = kem_wire_format.decode(encoded_pqc)
    assert dec_mode == Mode.PQC_ONLY
    assert dec_comps == tuple(pqc_comps)

    # 3. CLASSICAL_ONLY
    cls_comps = [("x25519", b"pub_cls" * 8, b"ct_cls" * 8)]
    encoded_cls = kem_wire_format.encode(Mode.CLASSICAL_ONLY, cls_comps)
    dec_mode, dec_comps = kem_wire_format.decode(encoded_cls)
    assert dec_mode == Mode.CLASSICAL_ONLY
    assert dec_comps == tuple(cls_comps)


def test_kem_wire_format_rejections() -> None:
    # Truncated buffer
    with pytest.raises(MalformedInputError):
        kem_wire_format.decode(b"\x01\x01")

    # Unknown version
    with pytest.raises(MalformedInputError):
        kem_wire_format.decode(b"\x99\x01\x02")

    # Length larger than buffer
    truncated = bytes.fromhex("010301000678323535313900000005aabb00000003010203")
    with pytest.raises(MalformedInputError):
        kem_wire_format.decode(truncated)

    # Trailing bytes
    trailing = bytes.fromhex("010301000678323535313900000002aabb00000003010203ff")
    with pytest.raises(MalformedInputError):
        kem_wire_format.decode(trailing)

    # Duplicate algorithms
    with pytest.raises(MalformedInputError):
        kem_wire_format.encode(
            Mode.HYBRID,
            [("x25519", b"p1", b"c1"), ("x25519", b"p2", b"c2")],
        )
