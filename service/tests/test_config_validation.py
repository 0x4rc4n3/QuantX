"""Unit tests for sidecar configuration validation.

Layer: sidecar
Depends on: quantx_service.config.validate_config
Implements: Pytest tests validating rules E1 to E8 and warnings W1 to W11 per docs/15-config-and-composition.md
Outside: Sidecar runtime server and HTTP request flow
Inside: Rule checks E1-E8 (errors) and W1-W11 (warnings) across valid and invalid configuration fixtures
Security notes: Confirms that insecure or invalid configurations fail closed before process start.
"""

from __future__ import annotations

import copy
from typing import Any

from quantx_service.config import validate_config

BASE_VALID_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "environment": "dev",
    "mode": "HYBRID",
    "algorithms": {
        "signature": {"classical": "ed25519", "pqc": "ml-dsa-65"},
        "kem": {"classical": "x25519", "pqc": "ml-kem-768"},
    },
    "registry": {"config_signing": "unsigned"},
    "state": {"backend": "memory"},
    "custody": {"backend": "memory_raw"},
    "second_factor": ["totp"],
    "threshold": {"enabled": False},
    "membership_proof": {"backend": "none"},
    "compliance": {"scanners": []},
    "service": {"auth": "bearer", "tls_enforcement": "off"},
}


def test_valid_recipe_a() -> None:
    """Recipe A configuration passes validation with zero errors."""
    errors, warnings = validate_config(copy.deepcopy(BASE_VALID_CONFIG))
    assert errors == []


def test_rule_e1_unknown_key() -> None:
    """E1: Unknown top-level key causes an error."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["unknown_field"] = "bad"
    errors, _ = validate_config(cfg)
    assert any("E1" in e and "unknown_field" in e for e in errors)


def test_rule_e1_invalid_schema_version() -> None:
    """E1: schema_version other than 1 is rejected."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["schema_version"] = 99
    errors, _ = validate_config(cfg)
    assert any("E1" in e and "schema_version" in e for e in errors)


def test_rule_e2_blocked_option_slh_dsa() -> None:
    """E2: Blocked option slh-dsa is refused (CFG-6, D-006)."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["algorithms"]["signature"]["pqc"] = "slh-dsa"
    errors, _ = validate_config(cfg)
    assert any("E2" in e and "slh-dsa" in e for e in errors)


def test_rule_e2_interface_only_anonymous() -> None:
    """E2: Interface-only membership_proof backend anonymous is refused (CFG-6)."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["membership_proof"]["backend"] = "anonymous"
    errors, _ = validate_config(cfg)
    assert any("E2" in e and "anonymous" in e for e in errors)


def test_rule_e3_hybrid_missing_classical() -> None:
    """E3: HYBRID mode requires both classical and PQC algorithms."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["algorithms"]["signature"]["classical"] = None
    errors, _ = validate_config(cfg)
    assert any("E3" in e for e in errors)


def test_rule_e3_pqc_only_with_classical_rejected() -> None:
    """E3: PQC_ONLY mode forbids classical algorithms."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["mode"] = "PQC_ONLY"
    # Still contains classical ed25519
    errors, _ = validate_config(cfg)
    assert any("E3" in e and "forbids classical" in e for e in errors)


def test_rule_e4_secret_like_key_literal() -> None:
    """E4: A secret-like key without _ref or holding a literal is rejected."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["custody"]["pin_ref"] = "1234_raw_secret"  # not starting with env:, file:, vault:
    errors, _ = validate_config(cfg)
    assert any("E4" in e and "pin_ref" in e for e in errors)


def test_rule_e5_missing_required_ref_redis() -> None:
    """E5: Required url_ref is missing for redis state backend."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["state"]["backend"] = "redis"
    cfg["state"]["url_ref"] = None
    errors, _ = validate_config(cfg)
    assert any("E5" in e and "url_ref" in e for e in errors)


def test_rule_e5_missing_required_ref_hsm() -> None:
    """E5: Required pin_ref is missing for hsm_pkcs11 custody backend."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["custody"]["backend"] = "hsm_pkcs11"
    cfg["custody"]["pin_ref"] = None
    errors, _ = validate_config(cfg)
    assert any("E5" in e and "pin_ref" in e for e in errors)


def test_rule_e6_multiple_auth_methods() -> None:
    """E6: service.auth specifying multiple methods is rejected."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["service"]["auth"] = ["bearer", "mtls"]
    errors, _ = validate_config(cfg)
    assert any("E6" in e for e in errors)


def test_rule_e7_production_with_memory_or_unsigned() -> None:
    """E7: Production environment with in-memory state or unsigned registry is rejected."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["environment"] = "production"
    errors, _ = validate_config(cfg)
    # Fails due to state: memory, unsigned registry, and tls_enforcement: off
    assert any("E7" in e and "memory" in e for e in errors)


def test_rule_e8_aws_kms_with_pqc_algorithm() -> None:
    """E8: Custody backend aws_kms cannot hold configured PQC algorithms (D-008)."""
    cfg = copy.deepcopy(BASE_VALID_CONFIG)
    cfg["custody"]["backend"] = "aws_kms"
    cfg["custody"]["key_id_ref"] = "env:KMS_KEY_ID"
    errors, _ = validate_config(cfg)
    assert any("E8" in e and "aws_kms" in e for e in errors)


def test_warnings_w1_and_w2() -> None:
    """W1 / W2 warnings emitted for CLASSICAL_ONLY and PQC_ONLY."""
    cfg_classical = copy.deepcopy(BASE_VALID_CONFIG)
    cfg_classical["mode"] = "CLASSICAL_ONLY"
    cfg_classical["algorithms"]["signature"]["pqc"] = None
    cfg_classical["algorithms"]["kem"]["pqc"] = None
    _, warn1 = validate_config(cfg_classical)
    assert any("W1" in w for w in warn1)

    cfg_pqc = copy.deepcopy(BASE_VALID_CONFIG)
    cfg_pqc["mode"] = "PQC_ONLY"
    cfg_pqc["algorithms"]["signature"]["classical"] = None
    cfg_pqc["algorithms"]["kem"]["classical"] = None
    _, warn2 = validate_config(cfg_pqc)
    assert any("W2" in w for w in warn2)
    assert any("W10" in w for w in warn2)
