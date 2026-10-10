"""Unit tests for TlsInspector certificate parsing and inspection.

Layer: 10
Depends on: quantx_compliance.scanners.tls_inspector.TlsInspector, cryptography.x509
Implements: Pytest tests validating in-process certificate parsing (FR-10.3) without openssl shell-out
Outside: Static code pattern scanning and SR-13 security assertions
Inside: Certificate DER parsing, signature algorithm and key size extraction, and subprocess check
Wire format: DER bytes in, CryptoBOM out
Security notes: Verifies in-process cryptography.x509 parsing; asserts no subprocess shell-out to openssl (FR-10.3)
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from quantx_compliance.scanners.tls_inspector import TlsInspector


def test_tls_inspector_parses_rsa_certificate(mock_rsa_cert_der: bytes) -> None:
    inspector = TlsInspector()

    # Ensure subprocess is never called during certificate parsing (FR-10.3)
    with patch("subprocess.run") as mock_run, patch("subprocess.Popen") as mock_popen:
        bom = inspector.parse_certificate_der(
            mock_rsa_cert_der,
            location="test-rsa.local:443",
            trust="verified",
        )
        assert not mock_run.called
        assert not mock_popen.called

    assert len(bom.findings) == 1
    finding = bom.findings[0]
    assert finding.source == "tls_inspect"
    assert "rsa" in finding.algorithm.lower()
    assert finding.key_size == 2048
    assert finding.location == "test-rsa.local:443"
    assert finding.trust == "verified"


def test_tls_inspector_parses_ec_certificate(mock_ec_cert_der: bytes) -> None:
    inspector = TlsInspector()
    bom = inspector.parse_certificate_der(
        mock_ec_cert_der,
        location="test-ec.local:443",
        trust="verified",
    )

    assert len(bom.findings) == 1
    finding = bom.findings[0]
    assert "ecdsa" in finding.algorithm.lower() or "sha256" in finding.algorithm.lower()
    assert finding.key_size == 256
    assert finding.trust == "verified"


def test_tls_inspector_invalid_mode_raises_value_error() -> None:
    inspector = TlsInspector()
    with pytest.raises(ValueError, match="Invalid mode"):
        inspector.inspect("example.com", mode="unsupported_mode")
