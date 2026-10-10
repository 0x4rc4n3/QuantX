"""Command-line interface for QuantX sidecar configuration and lifecycle.

Layer: sidecar
Depends on: quantx_service.config.load_config, quantx_service.config.validate_config, quantx_service.wiring.build_app_dependencies, quantx_service.main.create_app
Implements: main(argv) -> int subcommands init, validate, explain, run per docs/15-config-and-composition.md
Outside: Validation logic (config.py), object construction (wiring.py), HTTP routing (main.py)
Inside: Argument parsing, formatted console printing, backend probing, server process launching, and exit codes
Security notes: Never prints secret values; explain prints secret references and resolved class names only per CFG-5.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import yaml

from quantx_service.config import (
    ConfigValidationError,
    ServiceConfig,
    load_config,
    validate_config,
)
from quantx_service.main import create_app

RECIPE_TEMPLATES: dict[str, str] = {
    "A": """schema_version: 1
environment: dev
mode: HYBRID
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry: {config_signing: unsigned}
state: {backend: memory}
custody: {backend: memory_raw}
second_factor: [totp]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: []}
service: {auth: bearer, tls_enforcement: off}
""",
    "B": """schema_version: 1
environment: production
mode: HYBRID
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry: {config_signing: signed, signing_key_ref: "file:/etc/quantx/registry.pub"}
state: {backend: redis, url_ref: "env:QUANTX_REDIS_URL"}
custody:
  backend: hsm_pkcs11
  module_ref: "env:QUANTX_PKCS11_MODULE"
  slot_ref: "env:QUANTX_PKCS11_SLOT"
  pin_ref: "env:QUANTX_PKCS11_PIN"
second_factor: [totp, push]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: [source, tls_inspector]}
service: {auth: mtls, tls_enforcement: required}
""",
    "C": """schema_version: 1
environment: production
mode: PQC_ONLY
algorithms:
  signature: {pqc: ml-dsa-87}
  kem:       {pqc: ml-kem-1024}
registry: {config_signing: signed, signing_key_ref: "file:/etc/quantx/registry.pub"}
state: {backend: redis, url_ref: "env:QUANTX_REDIS_URL"}
custody:
  backend: hsm_pkcs11
  module_ref: "env:QUANTX_PKCS11_MODULE"
  slot_ref: "env:QUANTX_PKCS11_SLOT"
  pin_ref: "env:QUANTX_PKCS11_PIN"
second_factor: [totp]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: [source]}
service: {auth: mtls, tls_enforcement: required}
""",
}


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a starting quantx.yaml recipe."""
    recipe = str(args.recipe).upper()
    if recipe not in RECIPE_TEMPLATES:
        print(f"Error: Unknown recipe '{args.recipe}'. Available recipes: A, B, C", file=sys.stderr)
        return 2

    target_path = Path("quantx.yaml")
    if target_path.exists():
        print(
            f"Error: Target configuration file '{target_path}' already exists; refusing to overwrite",
            file=sys.stderr,
        )
        return 2

    target_path.write_text(RECIPE_TEMPLATES[recipe], encoding="utf-8")
    print(f"Initialized quantx.yaml using Recipe {recipe}.")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate configuration file against rules E1-E8 and W1-W11."""
    config_path = Path(args.file) if args.file else Path("quantx.yaml")
    if not config_path.is_file():
        print(f"Error: Config file not found: {config_path.resolve()}", file=sys.stderr)
        return 2

    try:
        content = config_path.read_text(encoding="utf-8")
        raw_dict = yaml.safe_load(content)
    except Exception as exc:
        print(f"Error parsing configuration YAML: {exc}", file=sys.stderr)
        return 2

    if not isinstance(raw_dict, dict):
        print("Error: Configuration root must be a YAML mapping", file=sys.stderr)
        return 2

    errors, warnings = validate_config(raw_dict, environment_override=args.env)

    for warn in warnings:
        print(f"WARN: {warn}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"\nValidation failed with {len(errors)} error(s).", file=sys.stderr)
        return 2

    print("Configuration is valid.")
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    """Explain resolved composition, option statuses, and hash without secrets."""
    config_path = Path(args.file) if args.file else Path("quantx.yaml")
    if not config_path.is_file():
        print(f"Error: Config file not found: {config_path.resolve()}", file=sys.stderr)
        return 2

    try:
        cfg = load_config(path=config_path)
    except ConfigValidationError as exc:
        print(f"Configuration validation failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Error reading configuration: {exc}", file=sys.stderr)
        return 2

    print("=== QuantX Resolved Composition ===")
    print(f"Canonical Config Hash (SHA-256): {cfg.canonical_hash}")
    print(f"Environment: {cfg.environment}")
    print(f"Operating Mode: {cfg.mode}")
    print("\nAlgorithms:")
    print(f"  Signature Classical: {cfg.algorithms.get('signature', {}).get('classical', 'None')}")
    print(f"  Signature PQC:       {cfg.algorithms.get('signature', {}).get('pqc', 'None')}")
    print(f"  KEM Classical:       {cfg.algorithms.get('kem', {}).get('classical', 'None')}")
    print(f"  KEM PQC:             {cfg.algorithms.get('kem', {}).get('pqc', 'None')}")
    print("\nBackends:")
    print(f"  State Store:         {cfg.state.get('backend', 'memory')}")
    print(f"  Key Custody:         {cfg.custody.get('backend', 'memory_raw')}")
    print(f"  Registry Signing:    {cfg.registry.get('config_signing', 'unsigned')}")
    print(f"  Service Auth:        {cfg.service.get('auth', 'bearer')}")
    print(f"  TLS Enforcement:     {cfg.service.get('tls_enforcement', 'off')}")

    if cfg.warnings:
        print("\nWarnings:")
        for w in cfg.warnings:
            print(f"  - {w}")

    return 0


def _probe_backends(cfg: ServiceConfig) -> bool:
    """Probe configured backends for reachability and algorithm support."""
    # Probe PQC support
    try:
        from cryptography.hazmat.primitives.asymmetric import (  # noqa: F401
            mldsa,
            mlkem,
        )
    except Exception:
        print(
            "Backend probe failed: Environment cryptography library lacks ML-DSA/ML-KEM support",
            file=sys.stderr,
        )
        return False

    # Probe Redis if configured
    if cfg.state.get("backend") == "redis":
        try:
            import redis

            url_ref = cfg.state.get("url_ref")
            from quantx_service.config import resolve_secret_ref

            redis_url = resolve_secret_ref(url_ref) if url_ref else None
            if not redis_url:
                print(
                    "Backend probe failed: Redis url_ref is missing or unresolvable",
                    file=sys.stderr,
                )
                return False
            client = redis.from_url(redis_url, socket_timeout=2.0)
            client.ping()
        except Exception as exc:
            print(f"Backend probe failed: Redis unreachable ({exc})", file=sys.stderr)
            return False

    # Probe PKCS#11 if configured
    if cfg.custody.get("backend") == "hsm_pkcs11":
        from quantx_service.config import resolve_secret_ref

        try:
            mod_ref = cfg.custody.get("module_ref")
            pin_ref = cfg.custody.get("pin_ref")
            mod_path = resolve_secret_ref(mod_ref) if mod_ref else None
            pin = resolve_secret_ref(pin_ref) if pin_ref else None
            if not mod_path or not pin:
                print(
                    "Backend probe failed: PKCS#11 module_ref or pin_ref not resolved",
                    file=sys.stderr,
                )
                return False
            if not Path(mod_path).exists():
                print(
                    f"Backend probe failed: PKCS#11 module library '{mod_path}' not found",
                    file=sys.stderr,
                )
                return False
        except Exception as exc:
            print(f"Backend probe failed: PKCS#11 probe error ({exc})", file=sys.stderr)
            return False

    return True


def cmd_run(args: argparse.Namespace) -> int:
    """Validate, probe backends, and start the sidecar server process."""
    config_path = Path(args.file) if args.file else Path("quantx.yaml")
    if not config_path.is_file():
        print(f"Error: Config file not found: {config_path.resolve()}", file=sys.stderr)
        return 2

    try:
        cfg = load_config(path=config_path)
    except ConfigValidationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Startup error: {exc}", file=sys.stderr)
        return 2

    # Probe backends (CFG-3 fail closed)
    if not _probe_backends(cfg):
        return 3

    try:
        import uvicorn

        fastapi_app = create_app(config=cfg)
        host = str(cfg.service.get("host", "127.0.0.1"))
        port = int(cfg.service.get("port", 8000))
        uvicorn.run(fastapi_app, host=host, port=port)
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 3

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI main entry point parsing arguments and dispatching commands."""
    parser = argparse.ArgumentParser(prog="quantx", description="QuantX PQC Sidecar CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize a starting quantx.yaml recipe")
    p_init.add_argument(
        "--recipe",
        choices=["A", "B", "C", "a", "b", "c"],
        default="A",
        help="Recipe template to initialize (A, B, or C)",
    )

    # validate
    p_validate = subparsers.add_parser(
        "validate", help="Validate configuration against rules E1-E8 and W1-W11"
    )
    p_validate.add_argument("--file", "-f", default=None, help="Path to configuration file")
    p_validate.add_argument(
        "--env", "-e", default=None, help="Environment override (dev, staging, production)"
    )

    # explain
    p_explain = subparsers.add_parser(
        "explain", help="Print resolved composition and hashes without secrets"
    )
    p_explain.add_argument("--file", "-f", default=None, help="Path to configuration file")

    # run
    p_run = subparsers.add_parser("run", help="Validate, probe backends, and start sidecar")
    p_run.add_argument("--file", "-f", default=None, help="Path to configuration file")

    args = parser.parse_args(argv)

    if args.subcommand == "init":
        return cmd_init(args)
    if args.subcommand == "validate":
        return cmd_validate(args)
    if args.subcommand == "explain":
        return cmd_explain(args)
    if args.subcommand == "run":
        return cmd_run(args)

    return 2


if __name__ == "__main__":
    sys.exit(main())
