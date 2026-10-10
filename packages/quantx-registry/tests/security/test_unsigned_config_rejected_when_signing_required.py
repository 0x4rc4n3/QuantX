"""
Layer: 3
Depends on: algorithm_registry.py, registry_config_signature.py
Implements: The mandatory foundational test for FR-3.3's signed-by-default rule.
Outside: Testing the signature math itself — that's test_registry_config_signature.py.
Inside: The load-time rejection behavior when signing is required and absent.
Security notes: This file IS the enforcement check for FR-3.3 / 09-auth-and-authorization.md. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_registry.algorithm_registry import AlgorithmRegistry


def test_unsigned_config_rejected_when_signing_required(example_config_path: Path) -> None:
    """
    FR-3.3: Attempt to load an unsigned config with allow_unsigned=False (the production default).
    Must fail at construction/load time with MalformedInputError, never deferred to resolve().
    """
    with pytest.raises(MalformedInputError) as exc_info:
        AlgorithmRegistry(
            config_path=example_config_path,
            allow_unsigned=False,
        )
    assert "Signed configuration required" in str(exc_info.value)


def test_signed_config_accepted_when_valid(signed_config_bundle: dict[str, Any]) -> None:
    """Verify that when signed properly, allow_unsigned=False loads successfully."""
    bundle = signed_config_bundle
    registry = AlgorithmRegistry(
        config_path=bundle["config_path"],
        allow_unsigned=False,
        config_signature=bundle["signature"],
        config_verifier=bundle["verifier"],
        canonicalizer=bundle["canonicalizer"],
    )
    sig_comb, kem_comb, mode = registry.resolve("session-auth")
    assert mode.value == "HYBRID"


def test_signed_config_rejected_on_corrupt_signature(signed_config_bundle: dict[str, Any]) -> None:
    """Verify that invalid/tampered signature on config raises MalformedInputError."""
    bundle = signed_config_bundle
    bad_sig = bytearray(bundle["signature"])
    bad_sig[0] ^= 0xFF

    with pytest.raises(MalformedInputError) as exc_info:
        AlgorithmRegistry(
            config_path=bundle["config_path"],
            allow_unsigned=False,
            config_signature=bytes(bad_sig),
            config_verifier=bundle["verifier"],
            canonicalizer=bundle["canonicalizer"],
        )
    assert "Configuration signature verification failed" in str(exc_info.value)
