"""
Layer: 2
Depends on: signature_wire_format.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies deterministic parsing, round-trip encoding, and bounds checking.
"""

from __future__ import annotations

import pytest
from quantx_combiners.signature import signature_wire_format
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode


def test_classical_signature_container_smoke_vector() -> None:
    """
    Test normative smoke vector from V2 §11:
    01030100076564323535313900000002aabb
    Decode as version 1, CLASSICAL_ONLY, one component with ed25519 and aabb.
    """
    raw_hex = "01030100076564323535313900000002aabb"
    wire_bytes = bytes.fromhex(raw_hex)

    mode, components = signature_wire_format.decode(wire_bytes)
    assert mode == Mode.CLASSICAL_ONLY
    assert len(components) == 1
    alg, sig = components[0]
    assert alg == "ed25519"
    assert sig == bytes.fromhex("aabb")

    # Round trip
    encoded = signature_wire_format.encode(mode, components)
    assert encoded == wire_bytes


def test_signature_wire_format_roundtrip_all_modes() -> None:
    # 1. HYBRID
    hybrid_comps = [("ed25519", b"sig1" * 16), ("ml-dsa-65", b"sig2" * 100)]
    encoded_hybrid = signature_wire_format.encode(Mode.HYBRID, hybrid_comps)
    dec_mode, dec_comps = signature_wire_format.decode(encoded_hybrid)
    assert dec_mode == Mode.HYBRID
    assert dec_comps == tuple(hybrid_comps)

    # 2. PQC_ONLY
    pqc_comps = [("ml-dsa-65", b"sig_pqc" * 50)]
    encoded_pqc = signature_wire_format.encode(Mode.PQC_ONLY, pqc_comps)
    dec_mode, dec_comps = signature_wire_format.decode(encoded_pqc)
    assert dec_mode == Mode.PQC_ONLY
    assert dec_comps == tuple(pqc_comps)

    # 3. CLASSICAL_ONLY
    cls_comps = [("ecdsa-p256", b"sig_cls" * 10)]
    encoded_cls = signature_wire_format.encode(Mode.CLASSICAL_ONLY, cls_comps)
    dec_mode, dec_comps = signature_wire_format.decode(encoded_cls)
    assert dec_mode == Mode.CLASSICAL_ONLY
    assert dec_comps == tuple(cls_comps)


def test_signature_wire_format_rejections() -> None:
    # Truncated header
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(b"\x01\x01")

    # Unknown version
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(
            b"\x02\x01\x02\x00\x01a\x00\x00\x00\x01b\x00\x01c\x00\x00\x00\x01d"
        )

    # Unknown mode
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(b"\x01\x05\x01\x00\x01a\x00\x00\x00\x01b")

    # Count mismatch (HYBRID declared with count 1)
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(b"\x01\x01\x01\x00\x01a\x00\x00\x00\x01b")

    # Truncated length claimed larger than buffer
    truncated = bytes.fromhex(
        "01030100076564323535313900000005aabb"
    )  # claims 5 bytes of sig, gives 2
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(truncated)

    # Trailing bytes
    valid_with_trailing = bytes.fromhex("01030100076564323535313900000002aabb" + "ff")
    with pytest.raises(MalformedInputError):
        signature_wire_format.decode(valid_with_trailing)

    # Duplicate algorithms
    with pytest.raises(MalformedInputError):
        signature_wire_format.encode(
            Mode.HYBRID,
            [("ed25519", b"sig1"), ("ed25519", b"sig2")],
        )
