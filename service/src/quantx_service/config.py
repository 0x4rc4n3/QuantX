"""Configuration and validation for QuantX REST sidecar.

Layer: sidecar
Depends on: quantx_core.canonicalization.jcs_canonicalizer.JCSCanonicalizer
Implements: load_config, validate_config, and ServiceConfig per docs/15-config-and-composition.md
Outside: Constructing concrete implementations from config (handled by wiring.py)
Inside: YAML parsing, strict validation of rules E1-E8, warning generation for W1-W11, and secret reference resolution
Security notes: Secret material is never hardcoded; all secrets are referenced via _ref keys (env:, file:, vault:) per CFG-4.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer

KNOWN_TOP_LEVEL_KEYS = {
    "schema_version",
    "environment",
    "mode",
    "algorithms",
    "registry",
    "state",
    "custody",
    "second_factor",
    "threshold",
    "membership_proof",
    "compliance",
    "service",
}

BLOCKED_OPTIONS = {"slh-dsa"}
INTERFACE_ONLY_OPTIONS = {"anonymous"}
VALID_MODES = {"HYBRID", "PQC_ONLY", "CLASSICAL_ONLY"}
VALID_ENVIRONMENTS = {"dev", "staging", "production"}

GATED_CUSTODY_BACKENDS = {
    "encrypted_file",
    "os_keychain",
    "hsm_pkcs11",
    "aws_kms",
    "gcp_kms",
}
SOFTWARE_CUSTODY_BACKENDS = {
    "memory_raw",
    "encrypted_file",
    "os_keychain",
}

PQC_SIGNATURE_ALGORITHMS = {"ml-dsa-65", "ml-dsa-87", "slh-dsa"}
PQC_KEM_ALGORITHMS = {"ml-kem-768", "ml-kem-1024"}
CLASSICAL_SIGNATURE_ALGORITHMS = {"ed25519", "ecdsa-p256"}
CLASSICAL_KEM_ALGORITHMS = {"x25519"}


class ConfigValidationError(Exception):
    """Raised when configuration fails validation rules."""

    def __init__(self, errors: list[str], warnings: list[str] | None = None) -> None:
        self.errors = errors
        self.warnings = warnings or []
        msg = f"Configuration validation failed with {len(errors)} error(s): " + "; ".join(errors)
        super().__init__(msg)


@dataclass
class ServiceConfig:
    """Parsed and validated QuantX service configuration."""

    schema_version: int
    environment: str
    mode: str
    algorithms: dict[str, Any]
    registry: dict[str, Any]
    state: dict[str, Any]
    custody: dict[str, Any]
    second_factor: list[str]
    threshold: dict[str, Any]
    membership_proof: dict[str, Any]
    compliance: dict[str, Any]
    service: dict[str, Any]
    raw_config: dict[str, Any] = field(default_factory=dict)
    canonical_hash: str = ""
    warnings: list[str] = field(default_factory=list)


def resolve_secret_ref(ref: str | None) -> str | None:
    """Resolve a secret reference from environment, file, or vault."""
    if ref is None:
        return None
    if not isinstance(ref, str):
        return None
    if ref.startswith("env:"):
        var_name = ref[4:]
        val = os.environ.get(var_name)
        if val is None:
            raise ValueError(f"Environment variable '{var_name}' referenced by '{ref}' is not set")
        return val
    if ref.startswith("file:"):
        path = Path(ref[5:])
        if not path.is_file():
            raise ValueError(f"Secret file '{path}' referenced by '{ref}' not found")
        return path.read_text(encoding="utf-8").strip()
    if ref.startswith("vault:"):
        raise ValueError("Vault references are not supported in this runtime environment")
    raise ValueError(f"Invalid secret reference format: '{ref}'")


def _is_valid_ref(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        return val.startswith("env:") or val.startswith("file:") or val.startswith("vault:")
    return False


def _check_secret_keys_recursive(obj: Any, path_prefix: str, errors: list[str]) -> None:
    """E4: Confirm secret-like keys end in _ref and hold valid references, not literals."""
    if not isinstance(obj, dict):
        return

    secret_like_patterns = [
        re.compile(r".*(?:password|secret|private_key|pin|token|credential).*", re.IGNORECASE),
    ]

    for k, v in obj.items():
        current_path = f"{path_prefix}.{k}" if path_prefix else str(k)
        if k.endswith("_ref"):
            if v is not None and not _is_valid_ref(v):
                errors.append(
                    f"E4: Secret reference key '{current_path}' must reference 'env:', 'file:', or 'vault:', got literal value"
                )
        else:
            # Check if this key appears to be a secret-like key without _ref
            for pattern in secret_like_patterns:
                if pattern.match(k):
                    errors.append(
                        f"E4: Secret-like key '{current_path}' must use a '_ref' suffix with a reference (e.g., '{k}_ref')"
                    )
                    break
        if isinstance(v, dict):
            _check_secret_keys_recursive(v, current_path, errors)


def validate_config(
    config: dict[str, Any],
    environment_override: str | None = None,
) -> tuple[list[str], list[str]]:
    """Validate configuration according to rules E1-E8 and generate warnings W1-W11.

    Returns:
        tuple of (errors, warnings)
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(config, dict):
        return (["E1: Configuration root must be a YAML mapping/dictionary"], [])

    # E1: Unknown key, wrong type or unsupported schema_version
    for k in config.keys():
        if k not in KNOWN_TOP_LEVEL_KEYS:
            errors.append(f"E1: Unknown top-level configuration key '{k}'")

    schema_version = config.get("schema_version")
    if schema_version != 1:
        errors.append(f"E1: Unsupported schema_version '{schema_version}'. Expected integer 1")

    env = environment_override or config.get("environment", "dev")
    if env not in VALID_ENVIRONMENTS:
        errors.append(
            f"E1: Invalid environment '{env}'. Expected one of {sorted(VALID_ENVIRONMENTS)}"
        )

    mode = config.get("mode", "HYBRID")
    if mode not in VALID_MODES:
        errors.append(f"E1: Invalid mode '{mode}'. Expected one of {sorted(VALID_MODES)}")

    algorithms = config.get("algorithms")
    if not isinstance(algorithms, dict):
        errors.append("E1: 'algorithms' must be a dictionary")
        algorithms = {}

    sig_algos = algorithms.get("signature") if isinstance(algorithms, dict) else {}
    kem_algos = algorithms.get("kem") if isinstance(algorithms, dict) else {}
    if not isinstance(sig_algos, dict):
        errors.append("E1: 'algorithms.signature' must be a dictionary")
        sig_algos = {}
    if not isinstance(kem_algos, dict):
        errors.append("E1: 'algorithms.kem' must be a dictionary")
        kem_algos = {}

    sig_classical = sig_algos.get("classical")
    sig_pqc = sig_algos.get("pqc")
    kem_classical = kem_algos.get("classical")
    kem_pqc = kem_algos.get("pqc")

    # E2: Blocked or interface-only option
    membership = config.get("membership_proof", {})
    if isinstance(membership, dict):
        mem_backend = membership.get("backend")
        if mem_backend in INTERFACE_ONLY_OPTIONS:
            errors.append(
                f"E2: Interface-only membership_proof backend '{mem_backend}' is refused (CFG-6)"
            )
        elif mem_backend in BLOCKED_OPTIONS:
            errors.append(f"E2: Blocked membership_proof backend '{mem_backend}' is refused")

    if sig_pqc in BLOCKED_OPTIONS:
        errors.append(f"E2: Blocked algorithm '{sig_pqc}' is refused (D-006)")
    if (
        sig_classical in BLOCKED_OPTIONS
        or kem_classical in BLOCKED_OPTIONS
        or kem_pqc in BLOCKED_OPTIONS
    ):
        errors.append("E2: Blocked algorithm selected")

    # E3: Algorithms match mode
    if mode == "HYBRID":
        if not sig_classical or not sig_pqc:
            errors.append("E3: HYBRID mode requires both classical and pqc signature algorithms")
        if not kem_classical or not kem_pqc:
            errors.append("E3: HYBRID mode requires both classical and pqc KEM algorithms")
    elif mode == "PQC_ONLY":
        if sig_classical is not None:
            errors.append(f"E3: PQC_ONLY mode forbids classical signature entry '{sig_classical}'")
        if kem_classical is not None:
            errors.append(f"E3: PQC_ONLY mode forbids classical KEM entry '{kem_classical}'")
        if not sig_pqc or not kem_pqc:
            errors.append("E3: PQC_ONLY mode requires both pqc signature and pqc KEM algorithms")
    elif mode == "CLASSICAL_ONLY":
        if sig_pqc is not None:
            errors.append(f"E3: CLASSICAL_ONLY mode forbids PQC signature entry '{sig_pqc}'")
        if kem_pqc is not None:
            errors.append(f"E3: CLASSICAL_ONLY mode forbids PQC KEM entry '{kem_pqc}'")
        if not sig_classical or not kem_classical:
            errors.append(
                "E3: CLASSICAL_ONLY mode requires both classical signature and classical KEM algorithms"
            )

    # E4: Secret references check
    _check_secret_keys_recursive(config, "", errors)

    # E5: Required references
    state = config.get("state", {})
    if isinstance(state, dict):
        state_backend = state.get("backend", "memory")
        if state_backend == "redis" and not state.get("url_ref"):
            errors.append("E5: Required reference 'url_ref' is missing for redis state backend")

    custody = config.get("custody", {})
    custody_backend = "memory_raw"
    if isinstance(custody, dict):
        custody_backend = custody.get("backend", "memory_raw")
        if custody_backend == "hsm_pkcs11" and not custody.get("pin_ref"):
            errors.append(
                "E5: Required reference 'pin_ref' is missing for hsm_pkcs11 custody backend"
            )
        if custody_backend in ("aws_kms", "gcp_kms") and not custody.get("key_id_ref"):
            errors.append(
                f"E5: Required reference 'key_id_ref' is missing for {custody_backend} custody backend"
            )

    registry = config.get("registry", {})
    reg_signing = "unsigned"
    if isinstance(registry, dict):
        reg_signing = registry.get("config_signing", "unsigned")
        if reg_signing == "signed" and not registry.get("signing_key_ref"):
            errors.append(
                "E5: Required reference 'signing_key_ref' is missing for signed registry configuration"
            )

    # E6: service.auth names more than one method
    service_conf = config.get("service", {})
    auth_val = None
    tls_enforcement = "off"
    if isinstance(service_conf, dict):
        auth_val = service_conf.get("auth", "bearer")
        tls_enforcement = service_conf.get("tls_enforcement", "off")
        if isinstance(auth_val, list):
            if len(auth_val) > 1:
                errors.append(
                    f"E6: service.auth names multiple methods {auth_val}; exactly one is permitted (D-016)"
                )
            auth_method = auth_val[0] if auth_val else "bearer"
        elif isinstance(auth_val, str):
            auth_method = auth_val
        else:
            errors.append("E1: service.auth must be a string or single-item list")
            auth_method = "bearer"

        if auth_method not in ("bearer", "mtls"):
            errors.append(
                f"E1: Unknown service.auth method '{auth_method}'. Expected 'bearer' or 'mtls'"
            )

        # D-016 fail-closed proxy check
        if service_conf.get("proxy_trust") or service_conf.get("external_tls_termination"):
            errors.append(
                "E1: External proxy TLS termination is forbidden; TLS must terminate in this service (D-016)"
            )

    # E7: environment: production checks
    if env == "production":
        if isinstance(state, dict) and state.get("backend") == "memory":
            errors.append("E7: production environment forbids in-memory state backend; use redis")
        if reg_signing == "unsigned":
            errors.append(
                "E7: production environment forbids unsigned registry; signed is required"
            )
        if tls_enforcement == "off":
            errors.append(
                "E7: production environment forbids tls_enforcement: off; required is required"
            )
        if custody_backend in SOFTWARE_CUSTODY_BACKENDS:
            errors.append(
                f"E7: production environment forbids software custody backend '{custody_backend}'; HSM or KMS is required (D-008)"
            )

    # E8: Custody algorithm capability check
    if custody_backend == "aws_kms":
        # AWS KMS does not support ML-DSA or ML-KEM algorithms
        pqc_in_use = [alg for alg in (sig_pqc, kem_pqc) if alg is not None]
        if pqc_in_use:
            errors.append(
                f"E8: Custody backend 'aws_kms' cannot hold configured PQC algorithm(s) {pqc_in_use} (D-008)"
            )

    # Warnings W1 - W11
    if mode == "CLASSICAL_ONLY":
        warnings.append(
            "W1: Mode is CLASSICAL_ONLY: no protection against harvest-now-decrypt-later (D2)"
        )
    elif mode == "PQC_ONLY":
        warnings.append(
            "W2: Mode is PQC_ONLY: no hybrid safety net, pyca PQC support is recent (D-006)"
        )
        warnings.append(
            "W10: Mode is PQC_ONLY: France (ANSSI) and Germany (BSI) do not accept standalone PQC during transition (D-017)"
        )

    # W3: Security level difference between signature and KEM
    high_sig = sig_pqc == "ml-dsa-87"
    high_kem = kem_pqc == "ml-kem-1024"
    if (high_sig and not high_kem) or (high_kem and not high_sig):
        warnings.append("W3: Signature and KEM are at different security levels")

    # W4: In-memory state with real custody or signed registry
    if isinstance(state, dict) and state.get("backend") == "memory":
        if custody_backend in GATED_CUSTODY_BACKENDS or reg_signing == "signed":
            warnings.append(
                "W4: In-memory state with real custody or signed registry: lost on restart, not shared"
            )

    # W5: Unsigned registry with hsm_pkcs11 or os_keychain
    if reg_signing == "unsigned" and custody_backend in ("hsm_pkcs11", "os_keychain"):
        warnings.append("W5: Unsigned registry with hardware/keychain custody")

    # W6: Software custody
    if custody_backend in SOFTWARE_CUSTODY_BACKENDS:
        warnings.append(
            f"W6: Software custody '{custody_backend}': private keys sit in application memory (dev and staging only, D-007)"
        )

    # W7: No second factor
    second_factors = config.get("second_factor", [])
    if not second_factors:
        warnings.append("W7: No second factor configured (D4)")

    # W8: Any gated option selected
    threshold = config.get("threshold", {})
    if (
        reg_signing == "signed"
        or custody_backend in GATED_CUSTODY_BACKENDS
        or (isinstance(threshold, dict) and threshold.get("enabled"))
        or (isinstance(membership, dict) and membership.get("backend") == "merkle")
    ):
        warnings.append(
            "W8: Gated option selected: needs independent review before production claim"
        )

    # W9: tls_enforcement: off outside production
    if env != "production" and tls_enforcement == "off":
        warnings.append("W9: tls_enforcement: off outside production (SR-13)")

    # W11: gcp_kms with ML-KEM
    if custody_backend == "gcp_kms" and kem_pqc in PQC_KEM_ALGORITHMS:
        warnings.append("W11: gcp_kms with ML-KEM algorithm: preview only (D-008)")

    return errors, warnings


def compute_canonical_config_hash(raw_config: dict[str, Any]) -> str:
    """Compute the SHA-256 hash of canonicalized configuration data (CFG-8)."""
    canonicalizer = JCSCanonicalizer()
    canonical_bytes = canonicalizer.canonicalize(raw_config)
    return hashlib.sha256(canonical_bytes).hexdigest()


def load_config(
    path: str | Path | None = None,
    environment_override: str | None = None,
) -> ServiceConfig:
    """Load, parse, validate, and compute canonical hash for quantx.yaml."""
    config_path: Path
    if path is not None:
        config_path = Path(path)
    else:
        env_path = os.environ.get("QUANTX_CONFIG")
        config_path = Path(env_path) if env_path else Path("quantx.yaml")

    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path.resolve()}")

    content = config_path.read_text(encoding="utf-8")
    raw_dict = yaml.safe_load(content)
    if not isinstance(raw_dict, dict):
        raise ConfigValidationError(["E1: Configuration root must be a YAML mapping"])

    errors, warnings = validate_config(raw_dict, environment_override=environment_override)
    if errors:
        raise ConfigValidationError(errors=errors, warnings=warnings)

    canonical_hash = compute_canonical_config_hash(raw_dict)

    env = environment_override or str(raw_dict.get("environment", "dev"))
    mode = str(raw_dict.get("mode", "HYBRID"))

    return ServiceConfig(
        schema_version=int(raw_dict.get("schema_version", 1)),
        environment=env,
        mode=mode,
        algorithms=raw_dict.get("algorithms", {}),
        registry=raw_dict.get("registry", {}),
        state=raw_dict.get("state", {}),
        custody=raw_dict.get("custody", {}),
        second_factor=list(raw_dict.get("second_factor", [])),
        threshold=raw_dict.get("threshold", {}),
        membership_proof=raw_dict.get("membership_proof", {}),
        compliance=raw_dict.get("compliance", {}),
        service=raw_dict.get("service", {}),
        raw_config=raw_dict,
        canonical_hash=canonical_hash,
        warnings=warnings,
    )
