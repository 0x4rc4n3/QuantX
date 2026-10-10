"""
Layer: 3
Depends on: registry_config_loader.py
Implements: pytest test functions.
Outside: Anything not directly under test here.
Inside: The scenarios in Required behavior.
Security notes: Safe YAML parsing tests, fails fast on unknown algorithms.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.types.mode import Mode
from quantx_registry import registry_config_loader


def test_registry_config_loader_valid(example_config_path: Path) -> None:
    roles = registry_config_loader.load(example_config_path)
    assert len(roles) == 3

    role_map = {r.role_id: r for r in roles}
    assert "session-auth" in role_map
    assert role_map["session-auth"].required_mode == Mode.HYBRID
    assert "session-auth-pqc-only" in role_map
    assert role_map["session-auth-pqc-only"].required_mode == Mode.PQC_ONLY
    assert "session-auth-classical-only" in role_map
    assert role_map["session-auth-classical-only"].required_mode == Mode.CLASSICAL_ONLY


def test_registry_config_loader_unknown_algorithm(tmp_path: Path) -> None:
    bad_yaml = """
roles:
  - role_id: "unknown-alg-role"
    mode: "CLASSICAL_ONLY"
    signature_algorithms:
      - "rsa-1024"
    kem_algorithms:
      - "x25519"
"""
    p = tmp_path / "bad.yaml"
    p.write_text(bad_yaml, encoding="utf-8")

    with pytest.raises(MalformedInputError) as exc_info:
        registry_config_loader.load(p)
    assert "unknown/unsupported signature algorithm" in str(exc_info.value)


def test_registry_config_loader_duplicate_role(tmp_path: Path) -> None:
    bad_yaml = """
roles:
  - role_id: "dup-role"
    mode: "CLASSICAL_ONLY"
    signature_algorithms: ["ed25519"]
    kem_algorithms: ["x25519"]
  - role_id: "dup-role"
    mode: "CLASSICAL_ONLY"
    signature_algorithms: ["ed25519"]
    kem_algorithms: ["x25519"]
"""
    p = tmp_path / "bad.yaml"
    p.write_text(bad_yaml, encoding="utf-8")

    with pytest.raises(MalformedInputError) as exc_info:
        registry_config_loader.load(p)
    assert "Duplicate role_id" in str(exc_info.value)
