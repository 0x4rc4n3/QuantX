"""Unit tests for ComplianceReportGenerator aggregation and rendering.

Layer: 10
Depends on: quantx_compliance.compliance_report_generator.ComplianceReportGenerator, quantx_compliance.crypto_bom_model.CryptoBOM
Implements: Pytest tests validating report generation from CryptoBOM findings without inventing facts (FR-10.4)
Outside: Scanner execution and raw network communication
Inside: Report assembly, trust tag preservation (SR-13), disclaimer preservation (SR-15), and unsupported standard detection
Wire format: In-memory test objects
Security notes: Asserts pure aggregation behavior (FR-10.4) and unverified/disclaimer tag pass-through
"""

from __future__ import annotations

from quantx_compliance.compliance_report_generator import (
    ComplianceReportGenerator,
)
from quantx_compliance.crypto_bom_model import STATIC_SCANNER_DISCLAIMER, CryptoBOM
from quantx_compliance.standards_catalog import StandardsCatalog


def test_compliance_report_generator_pure_aggregation(
    sample_crypto_bom: CryptoBOM,
    sample_standards_catalog: StandardsCatalog,
) -> None:
    generator = ComplianceReportGenerator(catalog=sample_standards_catalog)
    report = generator.generate(sample_crypto_bom)

    # Every fact in evaluated findings traces back to the input findings
    assert len(report.evaluated_findings) == len(sample_crypto_bom.findings)
    for ef in report.evaluated_findings:
        assert ef.finding in sample_crypto_bom.findings

    # Check trust-level tags survive into report unchanged (SR-13)
    trust_tags_in_bom = [f.trust for f in sample_crypto_bom.findings]
    trust_tags_in_report = [ef.finding.trust for ef in report.evaluated_findings]
    assert trust_tags_in_report == trust_tags_in_bom

    # Check disclaimer survives into report unchanged (SR-15)
    assert report.disclaimer == sample_crypto_bom.disclaimer
    markdown = report.render_markdown()
    assert STATIC_SCANNER_DISCLAIMER in markdown


def test_compliance_report_generator_reports_unrecognized_standard(
    sample_crypto_bom: CryptoBOM,
    sample_standards_catalog: StandardsCatalog,
) -> None:
    generator = ComplianceReportGenerator(catalog=sample_standards_catalog)
    report = generator.generate(
        sample_crypto_bom,
        target_standards=["FIPS-203", "NON-EXISTENT-STD-999"],
    )

    assert "NON-EXISTENT-STD-999" in report.unsupported_standards
    markdown = report.render_markdown()
    assert "No data for standard: `NON-EXISTENT-STD-999`" in markdown


def test_compliance_report_generator_to_dict(
    sample_crypto_bom: CryptoBOM,
    sample_standards_catalog: StandardsCatalog,
) -> None:
    generator = ComplianceReportGenerator(catalog=sample_standards_catalog)
    report = generator.generate(sample_crypto_bom)
    data = report.to_dict()

    assert "findings" in data
    assert "disclaimer" in data
    assert len(data["findings"]) == 3
