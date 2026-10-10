"""
Layer: 3
Depends on: RegistryRole (this package), PyYAML
Implements: load(path) -> list[RegistryRole] (pre-signature-verification, raw parse)
Outside: Verifying the config's signature — registry_config_signature.py's job; this file only parses structure.
Inside: Safe YAML parsing and validation into RegistryRole values.
Security notes: Uses yaml.safe_load exclusively — never yaml.load, preventing arbitrary code execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_core.types.mode import Mode

from quantx_registry.registry_role import RegistryRole


def parse_roles_data(data: Any) -> list[RegistryRole]:
    """Parse raw deserialized dictionary structure into RegistryRole objects."""
    if not isinstance(data, Mapping):
        raise MalformedInputError("Configuration root must be a YAML mapping")

    roles_data = data.get("roles")
    if not isinstance(roles_data, list):
        raise MalformedInputError("Configuration must contain a 'roles' list")

    parsed_roles: list[RegistryRole] = []
    seen_roles: set[str] = set()

    for item in roles_data:
        if not isinstance(item, Mapping):
            raise MalformedInputError("Each role entry must be a mapping")

        role_id = item.get("role_id")
        if not isinstance(role_id, str) or not role_id:
            raise MalformedInputError("Each role must specify a non-empty string 'role_id'")

        if role_id in seen_roles:
            raise MalformedInputError(f"Duplicate role_id: '{role_id}'")
        seen_roles.add(role_id)

        mode_str = item.get("mode")
        if not isinstance(mode_str, str):
            raise MalformedInputError(f"Role '{role_id}' missing 'mode'")
        try:
            mode = Mode(mode_str)
        except ValueError as exc:
            raise MalformedInputError(
                f"Role '{role_id}' has invalid mode '{mode_str}': {exc}"
            ) from exc

        sig_raw = item.get("signature_algorithms")
        if not isinstance(sig_raw, list):
            raise MalformedInputError(f"Role '{role_id}' missing 'signature_algorithms' list")

        kem_raw = item.get("kem_algorithms")
        if not isinstance(kem_raw, list):
            raise MalformedInputError(f"Role '{role_id}' missing 'kem_algorithms' list")

        sig_algs: list[AlgorithmId] = []
        for alg in sig_raw:
            try:
                sig_algs.append(AlgorithmId(alg))
            except ValueError as exc:
                raise MalformedInputError(
                    f"Role '{role_id}' references unknown/unsupported signature algorithm '{alg}': {exc}"
                ) from exc

        kem_algs: list[AlgorithmId] = []
        for alg in kem_raw:
            try:
                kem_algs.append(AlgorithmId(alg))
            except ValueError as exc:
                raise MalformedInputError(
                    f"Role '{role_id}' references unknown/unsupported KEM algorithm '{alg}': {exc}"
                ) from exc

        try:
            role = RegistryRole(
                role_id=role_id,
                required_mode=mode,
                signature_algorithms=tuple(sig_algs),
                kem_algorithms=tuple(kem_algs),
            )
        except (ValueError, TypeError) as exc:
            raise MalformedInputError(f"Invalid role definition for '{role_id}': {exc}") from exc

        parsed_roles.append(role)

    return parsed_roles


def load(path: Path | str) -> list[RegistryRole]:
    """
    Safely load algorithm registry configuration from a YAML file.
    Uses yaml.safe_load exclusively.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except Exception as exc:
        raise MalformedInputError(f"Failed to load or parse YAML configuration: {exc}") from exc

    return parse_roles_data(data)
