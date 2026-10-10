"""
Layer: 2
Depends on: Verifier (Layer 0), Mode (Layer 0), signature_wire_format.py, signature_mode_enforcement.py
Implements: verify(wire_bytes: bytes) -> bool — parses, enforces mode, then verifies
Outside: Wire encoding/decoding itself (signature_wire_format.py); the mode cross-check logic itself (signature_mode_enforcement.py) — this file calls both, holds neither's internals.
Inside: Orchestration: parse -> enforce mode -> verify each required component -> combine into one boolean result.
Security notes: Implements FR-2.3/SR-1 by delegating the actual mode check to signature_mode_enforcement.py and never proceeding to verification before that check passes. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

import struct
from typing import Mapping, Sequence

from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.mode import Mode

from quantx_combiners.signature import signature_mode_enforcement, signature_wire_format

DOMAIN_PREFIX: bytes = b"QuantX-SIG-v1\x00"

MODE_TO_BYTE: dict[Mode, int] = {
    Mode.HYBRID: 0x01,
    Mode.PQC_ONLY: 0x02,
    Mode.CLASSICAL_ONLY: 0x03,
}


def build_signed_payload(mode: Mode, role_id: str, message: bytes) -> bytes:
    """
    Construct normative D-009 signed payload:
    b"QuantX-SIG-v1\x00" || u8(mode) || u16(len(role_id)) || role_id_utf8 || u32(len(message)) || message
    """
    mode_byte = MODE_TO_BYTE[mode]
    role_bytes = role_id.encode("utf-8")
    # We pack mode_byte (u8), role_bytes_len (u16), message_len (u32)
    payload = bytearray()
    payload.extend(DOMAIN_PREFIX)
    payload.append(mode_byte)
    payload.extend(struct.pack(">H", len(role_bytes)))
    payload.extend(role_bytes)
    payload.extend(struct.pack(">I", len(message)))
    payload.extend(message)
    return bytes(payload)


class SignatureCombiner:
    """
    Generic SignatureCombiner orchestrating wire parsing, server-side mode enforcement,
    and delegating verification to configured Layer 0 Verifier instances (FR-2.1).
    """

    def __init__(
        self,
        required_mode: Mode,
        role_id: str,
        expected_algorithms: Sequence[str],
        verifiers: Mapping[str, Verifier],
    ) -> None:
        self._required_mode = required_mode
        self._role_id = role_id
        self._expected_algorithms = tuple(expected_algorithms)
        self._verifiers = dict(verifiers)

        # Validate that verifiers match expected_algorithms and count matches required_mode
        expected_cnt = 2 if required_mode == Mode.HYBRID else 1
        if len(self._expected_algorithms) != expected_cnt:
            raise ValueError(
                f"Expected algorithm count {len(self._expected_algorithms)} does not match mode {required_mode.value}"
            )
        for alg in self._expected_algorithms:
            if alg not in self._verifiers:
                raise ValueError(f"Missing Verifier for expected algorithm '{alg}'")

    @property
    def required_mode(self) -> Mode:
        return self._required_mode

    @property
    def role_id(self) -> str:
        return self._role_id

    @property
    def expected_algorithms(self) -> tuple[str, ...]:
        return self._expected_algorithms

    def verify(self, first: bytes, second: bytes) -> bool:
        """
        Verify the wire signature over the caller-supplied canonicalized message.
        Supports both (message, wire_signature) [standard Layer-0 Verifier order]
        and (wire_signature, message) [legacy combiner order].

        Returns True only if:
        1. Wire bytes decode cleanly.
        2. signature_mode_enforcement passes (declared_mode == required_mode).
        3. Parsed algorithms match expected algorithms in exact registry order.
        4. Every component verifier succeeds over the D-009 signed payload.

        Returns False on any internal error or mismatch, never raising.
        """
        # Distinguish which argument is wire_bytes: wire format starts with version 0x01 and mode byte <= 0x03
        # Try first as wire_bytes, second as message; if that fails to decode, try second as wire_bytes, first as message
        wire_bytes = first
        message = second
        try:
            declared_mode, components = signature_wire_format.decode(wire_bytes)
        except Exception:
            wire_bytes = second
            message = first
            try:
                declared_mode, components = signature_wire_format.decode(wire_bytes)
            except Exception:
                return False

        try:

            # Enforce mode strictly BEFORE calling any cryptographic verifier (SR-1)
            signature_mode_enforcement.enforce(
                declared_mode=declared_mode,
                required_mode=self._required_mode,
                parsed_components=components,
            )

            # Check that parsed components match expected algorithms and order
            parsed_algs = tuple(alg for alg, _ in components)
            if parsed_algs != self._expected_algorithms:
                return False

            signed_payload = build_signed_payload(
                mode=self._required_mode,
                role_id=self._role_id,
                message=message,
            )

            # Verify every component
            for alg_id, sig_bytes in components:
                verifier = self._verifiers[alg_id]
                if not verifier.verify(signed_payload, sig_bytes):
                    return False

            return True
        except Exception:
            return False
