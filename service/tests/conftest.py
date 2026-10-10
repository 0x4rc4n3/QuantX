"""Test fixtures for QuantX REST sidecar test suite.

Layer: sidecar
Depends on: quantx_service.main.create_app, quantx_service.wiring.build_app_dependencies, quantx_service.config.ServiceConfig
Implements: pytest fixtures for TestClient, sample keypairs, and in-memory environment
Outside: Individual test assertion logic
Inside: Initializing TestClient and in-memory backends for sidecar tests
Security notes: Test credentials and keys are ephemeral in-memory fixtures.
"""

from __future__ import annotations

from typing import Generator

import pytest
from quantx_core.interfaces.verifier import Verifier
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_service.config import ServiceConfig
from quantx_service.main import create_app
from quantx_service.wiring import build_app_dependencies
from starlette.testclient import TestClient


@pytest.fixture
def auth_keys() -> tuple[bytes, bytes, bytes, bytes]:
    """Generate ephemeral test keypairs (ed_priv, ed_pub, mldsa_priv, mldsa_pub)."""
    ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
    mldsa_priv, mldsa_pub = MlDsa65Adapter.generate_keypair()
    return ed_priv, ed_pub, mldsa_priv, mldsa_pub


@pytest.fixture
def recipe_a_config() -> ServiceConfig:
    """Provide a validated in-memory Recipe A configuration."""
    raw = {
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
    return ServiceConfig(
        schema_version=1,
        environment="dev",
        mode="HYBRID",
        algorithms=raw["algorithms"],
        registry=raw["registry"],
        state=raw["state"],
        custody=raw["custody"],
        second_factor=list(raw["second_factor"]),
        threshold=raw["threshold"],
        membership_proof=raw["membership_proof"],
        compliance=raw["compliance"],
        service=raw["service"],
        raw_config=raw,
        canonical_hash="test_hash_recipe_a",
    )


@pytest.fixture
def client(
    recipe_a_config: ServiceConfig,
    auth_keys: tuple[bytes, bytes, bytes, bytes],
) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient configured with in-memory Recipe A and sample verifiers."""
    ed_priv, ed_pub, mldsa_priv, mldsa_pub = auth_keys
    custom_verifiers: dict[str, dict[str, Verifier]] = {
        "session-auth": {
            "ed25519": Ed25519Adapter(public_key=ed_pub),
            "ml-dsa-65": MlDsa65Adapter(public_key=mldsa_pub),
        }
    }
    deps = build_app_dependencies(
        config=recipe_a_config,
        custom_verifiers_by_role=custom_verifiers,
    )
    app = create_app(dependencies=deps)
    with TestClient(app) as test_client:
        yield test_client
