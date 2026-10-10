"""
Layer: 3
Depends on: registry_role.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Tests immutability and role shape validation.
"""

from __future__ import annotations

import pytest
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_core.types.mode import Mode
from quantx_registry.registry_role import RegistryRole


def test_registry_role_creation_and_immutability() -> None:
    role = RegistryRole(
        role_id="test-hybrid",
        required_mode=Mode.HYBRID,
        signature_algorithms=(AlgorithmId.ED25519, AlgorithmId.ML_DSA_65),
        kem_algorithms=(AlgorithmId.X25519, AlgorithmId.ML_KEM_768),
    )

    assert role.role_id == "test-hybrid"
    assert role.required_mode == Mode.HYBRID
    assert len(role.signature_algorithms) == 2
    assert len(role.kem_algorithms) == 2

    # Check immutability
    with pytest.raises((AttributeError, TypeError)):
        role.role_id = "new-id"  # type: ignore[misc]


def test_registry_role_validation_failures() -> None:
    # Empty role_id
    with pytest.raises(ValueError):
        RegistryRole(
            role_id="",
            required_mode=Mode.CLASSICAL_ONLY,
            signature_algorithms=(AlgorithmId.ED25519,),
            kem_algorithms=(AlgorithmId.X25519,),
        )

    # Count mismatch for HYBRID (needs 2, given 1)
    with pytest.raises(ValueError):
        RegistryRole(
            role_id="bad-count",
            required_mode=Mode.HYBRID,
            signature_algorithms=(AlgorithmId.ED25519,),
            kem_algorithms=(AlgorithmId.X25519,),
        )

    # Duplicate algorithms
    with pytest.raises(ValueError):
        RegistryRole(
            role_id="dup-alg",
            required_mode=Mode.HYBRID,
            signature_algorithms=(AlgorithmId.ED25519, AlgorithmId.ED25519),
            kem_algorithms=(AlgorithmId.X25519, AlgorithmId.ML_KEM_768),
        )
