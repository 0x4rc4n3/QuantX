"""
Layer: 3
Depends on: Mode, AlgorithmId (Layer 0)
Implements: RegistryRole
Outside: Loading/parsing the YAML file itself (registry_config_loader.py); resolving to combiners (algorithm_registry.py).
Inside: Value type mapping role_id to signature and KEM algorithm pairings and required_mode.
Security notes: Immutable value type once constructed; required_mode is fixed server-side.
"""

from __future__ import annotations

from dataclasses import dataclass

from quantx_core.types.algorithm_id import AlgorithmId
from quantx_core.types.mode import Mode


@dataclass(frozen=True)
class RegistryRole:
    """
    Immutable value type representing a configured algorithm registry role.
    """

    role_id: str
    required_mode: Mode
    signature_algorithms: tuple[AlgorithmId, ...]
    kem_algorithms: tuple[AlgorithmId, ...]

    def __post_init__(self) -> None:
        if not self.role_id:
            raise ValueError("role_id must be a non-empty string")

        if not isinstance(self.required_mode, Mode):
            raise TypeError(
                f"required_mode must be an instance of Mode, got {type(self.required_mode)}"
            )

        expected_count = 2 if self.required_mode == Mode.HYBRID else 1

        if len(self.signature_algorithms) != expected_count:
            raise ValueError(
                f"signature_algorithms count {len(self.signature_algorithms)} does not match mode {self.required_mode.value} (expected {expected_count})"
            )

        if len(self.kem_algorithms) != expected_count:
            raise ValueError(
                f"kem_algorithms count {len(self.kem_algorithms)} does not match mode {self.required_mode.value} (expected {expected_count})"
            )

        if len(set(self.signature_algorithms)) != len(self.signature_algorithms):
            raise ValueError("Duplicate algorithm in signature_algorithms")

        if len(set(self.kem_algorithms)) != len(self.kem_algorithms):
            raise ValueError("Duplicate algorithm in kem_algorithms")
