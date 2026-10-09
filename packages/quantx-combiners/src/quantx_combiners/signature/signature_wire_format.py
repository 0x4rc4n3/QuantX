"""
Layer: 2
Depends on: Mode, MalformedInputError (Layer 0)
Implements: encode(mode, components) -> bytes; decode(wire_bytes) -> (declared_mode, parsed_components)
Outside: Deciding whether the parsed declared_mode is acceptable — that's signature_mode_enforcement.py's job entirely; this file has no opinion on acceptance.
Inside: Length-prefixed binary framing: reading/writing each component's declared length and bytes.
Wire format: Versioned length-prefixed binary defined normatively in docs/QUANTX-V2-ARCHITECTURE.md §5: version byte, mode byte, component count, and ordered algorithm-ID/signature components with bounded big-endian lengths. Unknown versions, malformed lengths, duplicate algorithms, invalid UTF-8, mode/count mismatches, and trailing bytes are rejected.
Security notes: Carries no acceptance-decision authority by design — parses shape only.
"""

from __future__ import annotations

import struct
from typing import Sequence, Tuple

from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode

WIRE_VERSION: int = 0x01

# Mode to byte mapping and reverse
MODE_TO_BYTE: dict[Mode, int] = {
    Mode.HYBRID: 0x01,
    Mode.PQC_ONLY: 0x02,
    Mode.CLASSICAL_ONLY: 0x03,
}

BYTE_TO_MODE: dict[int, Mode] = {
    0x01: Mode.HYBRID,
    0x02: Mode.PQC_ONLY,
    0x03: Mode.CLASSICAL_ONLY,
}

MAX_ALG_ID_LEN: int = 64
MAX_SIG_LEN: int = 1_048_576


def encode(
    mode: Mode,
    components: Sequence[Tuple[str, bytes]],
) -> bytes:
    """Encode mode and signature components into versioned wire bytes."""
    if mode not in MODE_TO_BYTE:
        raise MalformedInputError(f"Unsupported mode: {mode}")

    mode_byte = MODE_TO_BYTE[mode]
    expected_count = 2 if mode == Mode.HYBRID else 1
    if len(components) != expected_count:
        raise MalformedInputError(
            f"Component count {len(components)} does not match mode {mode.value} (expected {expected_count})"
        )

    out = bytearray()
    out.append(WIRE_VERSION)
    out.append(mode_byte)
    out.append(len(components))

    seen_algs: set[str] = set()
    for alg_id, sig_bytes in components:
        if not isinstance(alg_id, str):
            raise MalformedInputError("Algorithm ID must be a string")
        if not alg_id or alg_id != alg_id.lower():
            raise MalformedInputError(f"Algorithm ID must be non-empty and lowercase: {alg_id}")
        if alg_id in seen_algs:
            raise MalformedInputError(f"Duplicate algorithm ID: {alg_id}")
        seen_algs.add(alg_id)

        try:
            alg_bytes = alg_id.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise MalformedInputError(f"Algorithm ID is not valid UTF-8: {exc}") from exc

        if not (1 <= len(alg_bytes) <= MAX_ALG_ID_LEN):
            raise MalformedInputError(
                f"Algorithm ID length {len(alg_bytes)} out of bounds (1..{MAX_ALG_ID_LEN})"
            )

        if not (1 <= len(sig_bytes) <= MAX_SIG_LEN):
            raise MalformedInputError(
                f"Signature length {len(sig_bytes)} out of bounds (1..{MAX_SIG_LEN})"
            )

        out.extend(struct.pack(">H", len(alg_bytes)))
        out.extend(alg_bytes)
        out.extend(struct.pack(">I", len(sig_bytes)))
        out.extend(sig_bytes)

    return bytes(out)


def decode(
    wire_bytes: bytes,
) -> tuple[Mode, tuple[tuple[str, bytes], ...]]:
    """
    Decode versioned wire bytes into declared Mode and signature components.

    Bounds-checks every length against remaining buffer before slicing.
    Rejects malformed lengths, invalid version, duplicate algs, invalid UTF-8,
    mode/count mismatches, and trailing bytes.
    """
    if not isinstance(wire_bytes, (bytes, bytearray)):
        raise MalformedInputError("Wire input must be bytes")

    buf = memoryview(wire_bytes)
    total_len = len(buf)

    if total_len < 3:
        raise MalformedInputError("Wire bytes truncated: header requires at least 3 bytes")

    version = buf[0]
    if version != WIRE_VERSION:
        raise MalformedInputError(f"Unsupported wire format version: {version:#04x}")

    mode_byte = buf[1]
    if mode_byte not in BYTE_TO_MODE:
        raise MalformedInputError(f"Unknown mode byte: {mode_byte:#04x}")
    declared_mode = BYTE_TO_MODE[mode_byte]

    component_cnt = buf[2]
    expected_cnt = 2 if declared_mode == Mode.HYBRID else 1
    if component_cnt != expected_cnt:
        raise MalformedInputError(
            f"Component count {component_cnt} does not match mode {declared_mode.value} (expected {expected_cnt})"
        )

    offset = 3
    components: list[tuple[str, bytes]] = []
    seen_algs: set[str] = set()

    for _ in range(component_cnt):
        # Read alg_id_len (u16)
        if offset + 2 > total_len:
            raise MalformedInputError("Truncated buffer while reading algorithm_id_len")
        (alg_len,) = struct.unpack(">H", buf[offset : offset + 2])
        offset += 2

        if not (1 <= alg_len <= MAX_ALG_ID_LEN):
            raise MalformedInputError(
                f"algorithm_id_len {alg_len} out of bounds (1..{MAX_ALG_ID_LEN})"
            )

        if offset + alg_len > total_len:
            raise MalformedInputError("Truncated buffer while reading algorithm_id")
        alg_raw = bytes(buf[offset : offset + alg_len])
        offset += alg_len

        try:
            alg_id = alg_raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MalformedInputError(f"algorithm_id is not valid UTF-8: {exc}") from exc

        if alg_id != alg_id.lower():
            raise MalformedInputError(f"algorithm_id must be lowercase ASCII-compatible: {alg_id}")

        if alg_id in seen_algs:
            raise MalformedInputError(f"Duplicate algorithm_id: {alg_id}")
        seen_algs.add(alg_id)

        # Read signature_len (u32)
        if offset + 4 > total_len:
            raise MalformedInputError("Truncated buffer while reading signature_len")
        (sig_len,) = struct.unpack(">I", buf[offset : offset + 4])
        offset += 4

        if not (1 <= sig_len <= MAX_SIG_LEN):
            raise MalformedInputError(f"signature_len {sig_len} out of bounds (1..{MAX_SIG_LEN})")

        if offset + sig_len > total_len:
            raise MalformedInputError("Truncated buffer while reading signature")
        sig_bytes = bytes(buf[offset : offset + sig_len])
        offset += sig_len

        components.append((alg_id, sig_bytes))

    if offset != total_len:
        raise MalformedInputError(
            f"Extraneous trailing bytes: read {offset} bytes out of {total_len}"
        )

    return declared_mode, tuple(components)
