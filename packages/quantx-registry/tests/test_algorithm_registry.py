"""
Layer: 3
Depends on: algorithm_registry.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Verifies correct resolution to combiners and required_mode.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from quantx_core.types.mode import Mode
from quantx_registry.algorithm_registry import AlgorithmRegistry


def test_algorithm_registry_resolve_unsigned_dev(example_config_path: Path) -> None:
    registry = AlgorithmRegistry(config_path=example_config_path, allow_unsigned=True)

    sig_comb, kem_comb, mode = registry.resolve("session-auth")
    assert mode == Mode.HYBRID
    assert sig_comb.required_mode == Mode.HYBRID
    assert kem_comb.required_mode == Mode.HYBRID
    assert sig_comb.expected_algorithms == ("ed25519", "ml-dsa-65")
    assert kem_comb.expected_algorithms == ("x25519", "ml-kem-768")


def test_algorithm_registry_unknown_role(example_config_path: Path) -> None:
    registry = AlgorithmRegistry(config_path=example_config_path, allow_unsigned=True)
    with pytest.raises(KeyError):
        registry.resolve("non-existent-role")
