"""
Layer: 3
Depends on: Every file in this package.
Implements: pytest fixtures.
Outside: Assertions.
Inside: Fixture construction: signed/unsigned config variants.
Security notes: The unsigned-config fixture is what makes test_unsigned_config_rejected_when_signing_required.py a real test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_registry import registry_config_signature


@pytest.fixture
def example_config_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    path = repo_root / "config" / "algorithm_registry.example.yaml"
    return path


@pytest.fixture
def signed_config_bundle(example_config_path: Path, tmp_path: Path) -> dict[str, Any]:
    content = example_config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    priv_key, pub_key = Ed25519Adapter.generate_keypair()
    signer = Ed25519Adapter(private_key=priv_key)
    verifier = Ed25519Adapter(public_key=pub_key)
    canonicalizer = JCSCanonicalizer()

    signature = registry_config_signature.sign(
        config_data=data,
        signer=signer,
        canonicalizer=canonicalizer,
    )

    config_file = tmp_path / "signed_registry.yaml"
    config_file.write_text(content, encoding="utf-8")

    return {
        "config_path": config_file,
        "config_data": data,
        "signature": signature,
        "verifier": verifier,
        "signer": signer,
        "canonicalizer": canonicalizer,
    }
