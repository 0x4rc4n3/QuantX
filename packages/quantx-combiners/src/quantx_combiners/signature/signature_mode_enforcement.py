"""
Layer: 2
Depends on: Mode (Layer 0 type)
Implements: enforce(declared_mode: Mode, required_mode: Mode, parsed_components) -> None — raises/rejects on mismatch, otherwise returns normally
Outside: Parsing wire bytes (signature_wire_format.py); verifying the actual signature components (signature_combiner.py, via the underlying Verifiers)
Inside: The mode cross-check itself, and only that
Security notes: Implements SR-1 in full. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from typing import Any, Sequence

from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode


def enforce(
    declared_mode: Mode,
    required_mode: Mode,
    parsed_components: Sequence[Any],
) -> None:
    """
    Enforce that declared mode from wire strictly matches server required_mode (SR-1).

    If declared_mode != required_mode, or if parsed_components count does not match
    the required mode specification, raises MalformedInputError unconditionally before
    any cryptographic verification can be invoked.
    """
    if declared_mode != required_mode:
        raise MalformedInputError(
            f"Mode mismatch: declared wire mode '{declared_mode.value}' does not match required mode '{required_mode.value}'"
        )

    expected_count = 2 if required_mode == Mode.HYBRID else 1
    if len(parsed_components) != expected_count:
        raise MalformedInputError(
            f"Component count {len(parsed_components)} does not match required mode '{required_mode.value}' (expected {expected_count})"
        )
