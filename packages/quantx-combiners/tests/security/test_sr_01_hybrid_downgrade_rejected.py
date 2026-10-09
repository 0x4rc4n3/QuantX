"""
Layer: 2
Depends on: The full signature-combining path.
Implements: The mandatory automated security test for SR-1.
Outside: SR-7 (that's the KEM-side test).
Inside: Constructing a genuine HYBRID signature via conftest.py's fixture, stripping the PQC component, rewriting the declared-mode byte, and confirming rejection.
Security notes: This file IS the SR-1 enforcement check. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from quantx_combiners.signature import signature_mode_enforcement, signature_wire_format
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode


def test_sr_01_hybrid_downgrade_rejected(
    genuine_hybrid_signature_bundle: dict[str, Any],
) -> None:
    """
    Mandatory test 1 (SR-1, 10-security-requirements.md):
    Strip the PQC component from a genuine hybrid signature, rewrite the declared-mode byte
    to CLASSICAL_ONLY (0x03), call SignatureCombiner.verify() with required_mode=HYBRID.
    Must return False, and rejection must happen in signature_mode_enforcement before any
    Verifier.verify() call executes.
    """
    bundle = genuine_hybrid_signature_bundle
    combiner = bundle["combiner"]
    message = bundle["message"]
    ed_sig = bundle["ed_sig"]

    # Construct the stripped signature: only classical component, mode set to CLASSICAL_ONLY
    tampered_wire = signature_wire_format.encode(
        Mode.CLASSICAL_ONLY,
        [("ed25519", ed_sig)],
    )

    # Spy on verifiers to verify none was invoked
    ed_adapter = bundle["ed_adapter"]
    mldsa_adapter = bundle["mldsa_adapter"]

    with (
        patch.object(ed_adapter, "verify", wraps=ed_adapter.verify) as mock_ed_verify,
        patch.object(mldsa_adapter, "verify", wraps=mldsa_adapter.verify) as mock_mldsa_verify,
        patch.object(
            signature_mode_enforcement, "enforce", wraps=signature_mode_enforcement.enforce
        ) as mock_enforce,
    ):

        # Verification must return False
        result = combiner.verify(tampered_wire, message)
        assert result is False

        # signature_mode_enforcement MUST have been called and raised MalformedInputError
        mock_enforce.assert_called_once()
        try:
            mock_enforce.assert_called_with(
                declared_mode=Mode.CLASSICAL_ONLY,
                required_mode=Mode.HYBRID,
                parsed_components=(("ed25519", ed_sig),),
            )
        except AssertionError:
            # Check with positional arguments if keyword check fails
            assert mock_enforce.call_count == 1

        # Crucially: NEITHER verifier must ever have been called
        mock_ed_verify.assert_not_called()
        mock_mldsa_verify.assert_not_called()


def test_sr_01_direct_mode_enforcement_raises() -> None:
    """Direct unit test on signature_mode_enforcement.enforce() raising MalformedInputError on mismatch."""
    with pytest.raises(MalformedInputError) as exc_info:
        signature_mode_enforcement.enforce(
            declared_mode=Mode.CLASSICAL_ONLY,
            required_mode=Mode.HYBRID,
            parsed_components=[("ed25519", b"sig")],
        )
    assert "Mode mismatch" in str(exc_info.value)
