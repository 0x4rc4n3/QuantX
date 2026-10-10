"""Shared test fixtures for quantx-compliance test suites.

Layer: 10
Depends on: quantx_compliance.crypto_bom_model, quantx_compliance.standards_catalog
Implements: Pytest fixtures for CryptoBOM instances, mock certificates, and temporary source trees
Outside: Test assertion logic
Inside: Shared test fixture definitions
Wire format: In-memory test objects
Security notes: Test harness only; provides unverified and verified findings for SR-13 and disclaimer fixtures for SR-15
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID
from quantx_compliance.crypto_bom_model import (
    STATIC_SCANNER_DISCLAIMER,
    CryptoBOM,
    CryptoBOMFinding,
)
from quantx_compliance.standards_catalog import StandardsCatalog
from quantx_core.types.algorithm_id import AlgorithmId


@pytest.fixture
def sample_standards_catalog() -> StandardsCatalog:
    return StandardsCatalog()


@pytest.fixture
def sample_crypto_bom() -> CryptoBOM:
    bom = CryptoBOM(disclaimer=STATIC_SCANNER_DISCLAIMER)
    bom.add_finding(
        CryptoBOMFinding(
            finding_id="find-001",
            source="static_scan",
            algorithm=AlgorithmId.ML_KEM_768,
            key_size=None,
            location="src/crypto.py:42",
            trust="unverified",
            disclaimer=STATIC_SCANNER_DISCLAIMER,
        )
    )
    bom.add_finding(
        CryptoBOMFinding(
            finding_id="find-002",
            source="tls_inspect",
            algorithm="sha256WithRSAEncryption",
            key_size=2048,
            location="api.internal:443",
            trust="verified",
            disclaimer=None,
        )
    )
    bom.add_finding(
        CryptoBOMFinding(
            finding_id="find-003",
            source="tls_inspect",
            algorithm="ecdsa-with-SHA256",
            key_size=256,
            location="untrusted-dev:8443",
            trust="unverified",
            disclaimer=None,
        )
    )
    return bom


@pytest.fixture
def temp_source_tree(tmp_path: Path) -> Path:
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    file1 = src_dir / "key_exchange.py"
    file1.write_text(
        """
import os
# Using post-quantum KEM
algorithm = 'ml-kem-768'
fallback = 'x25519'
symmetric_cipher = 'aes-256-gcm'
""",
        encoding="utf-8",
    )

    file2 = src_dir / "signatures.py"
    file2.write_text(
        """
from quantx_crypto_adapters import MlDsa65Adapter
sig_scheme = 'ml-dsa-65'
legacy = 'rsa-2048'
hasher = 'sha-256'
""",
        encoding="utf-8",
    )

    return src_dir


@pytest.fixture
def mock_rsa_cert_der() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "mock.local")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1000)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


@pytest.fixture
def mock_ec_cert_der() -> bytes:
    key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "mock-ec.local")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1001)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)
