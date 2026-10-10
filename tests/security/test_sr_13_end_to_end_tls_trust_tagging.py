"""End-to-end security test for SR-13: TLS findings tagged by trust level through to compliance report.

Layer: cross-cutting
Depends on: quantx_compliance.scanners.tls_inspector.TlsInspector, quantx_compliance.compliance_report_generator.ComplianceReportGenerator, quantx_compliance.crypto_bom_model.CryptoBOM
Implements: Mandatory full-stack end-to-end test for SR-13 (TLS findings tagged by trust level survive into final report)
Outside: Every other numbered SR item
Inside: Parse certificates from verified and permissive probes, feed both into ComplianceReportGenerator, and confirm tags survive
Wire format: CryptoBOM and report structures
Security notes: Mandatory SR-13 end-to-end confirmation spanning quantx-compliance
"""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from quantx_compliance.compliance_report_generator import ComplianceReportGenerator
from quantx_compliance.crypto_bom_model import CryptoBOM
from quantx_compliance.scanners.tls_inspector import TlsInspector


@pytest.fixture
def mock_der_cert() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "test.local")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


def test_sr_13_end_to_end_tls_trust_tagging_survives_into_report(mock_der_cert: bytes) -> None:
    inspector = TlsInspector()

    # 1. Inspect verified authenticated finding
    verified_bom = inspector.parse_certificate_der(
        mock_der_cert,
        location="auth.corp.com:443",
        trust="verified",
    )

    # 2. Inspect permissive unverified finding
    unverified_bom = inspector.parse_certificate_der(
        mock_der_cert,
        location="unverified-dev.corp.com:443",
        trust="unverified",
    )

    # 3. Aggregate into single BOM
    combined_bom = CryptoBOM()
    for f in verified_bom.findings:
        combined_bom.add_finding(f)
    for f in unverified_bom.findings:
        combined_bom.add_finding(f)

    # 4. Generate compliance report
    generator = ComplianceReportGenerator()
    report = generator.generate(combined_bom)

    # 5. Confirm trust level tags survive into report findings and rendered markdown (SR-13)
    assert len(report.evaluated_findings) == 2
    trust_tags = {ef.finding.location: ef.finding.trust for ef in report.evaluated_findings}
    assert trust_tags["auth.corp.com:443"] == "verified"
    assert trust_tags["unverified-dev.corp.com:443"] == "unverified"

    markdown = report.render_markdown()
    assert "**verified**" in markdown
    assert "**unverified**" in markdown
