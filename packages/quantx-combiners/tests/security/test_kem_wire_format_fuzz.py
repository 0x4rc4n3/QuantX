"""
Layer: 2
Depends on: kem_wire_format.py
Implements: The mandatory automated wire-parser fuzz test category.
Outside: Deterministic regression cases — see the matching test_{wf} file.
Inside: Hypothesis-generated malformed/truncated/adversarially-sized inputs against decode().
Security notes: Feeds SR-7's wire-parsing precondition — a parser that mishandles a malformed length field here is a precondition for the combiner-level SR item ever running correctly.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
from quantx_combiners.kem import kem_wire_format
from quantx_core.exceptions.malformed_input_error import MalformedInputError


@settings(max_examples=200, deadline=None)
@given(st.binary(min_size=0, max_size=1024))
def test_kem_wire_format_fuzz_random_bytes(data: bytes) -> None:
    """
    Hypothesis fuzz test: random bytes fed into kem_wire_format.decode()
    MUST either parse cleanly into (Mode, components) or raise MalformedInputError.
    It MUST NEVER raise any unhandled exceptions, crash, or do out-of-bounds reads.
    """
    try:
        mode, components = kem_wire_format.decode(data)
        assert mode is not None
        assert isinstance(components, tuple)
    except MalformedInputError:
        pass


@settings(max_examples=100, deadline=None)
@given(
    version=st.integers(min_value=0, max_value=255),
    mode_byte=st.integers(min_value=0, max_value=255),
    count=st.integers(min_value=0, max_value=255),
    alg_len=st.integers(min_value=0, max_value=65535),
    pub_len=st.integers(min_value=0, max_value=10_000_000),
    ct_len=st.integers(min_value=0, max_value=10_000_000),
    payload=st.binary(min_size=0, max_size=256),
)
def test_kem_wire_format_fuzz_structured_adversarial_lengths(
    version: int,
    mode_byte: int,
    count: int,
    alg_len: int,
    pub_len: int,
    ct_len: int,
    payload: bytes,
) -> None:
    """
    Fuzz test with crafted headers containing adversarial/oversized lengths.
    """
    import struct

    header = bytes([version, mode_byte, count])
    crafted = (
        header
        + struct.pack(">H", alg_len)
        + payload[: min(len(payload), 32)]
        + struct.pack(">I", pub_len)
        + payload[: min(len(payload), 32)]
        + struct.pack(">I", ct_len)
        + payload
    )

    try:
        kem_wire_format.decode(crafted)
    except MalformedInputError:
        pass
