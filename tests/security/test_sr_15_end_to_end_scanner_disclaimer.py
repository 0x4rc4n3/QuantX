"""End-to-end security test for SR-15: Static scanner disclaimer survives into compliance report.

Layer: cross-cutting
Depends on: quantx_compliance.scanners.static_source_scanner.StaticSourceScanner, quantx_compliance.compliance_report_generator.ComplianceReportGenerator, quantx_compliance.crypto_bom_model.STATIC_SCANNER_DISCLAIMER
Implements: Mandatory full-stack end-to-end test for SR-15 (static scanner disclaimer survives aggregation)
Outside: Every other numbered SR item
Inside: Run StaticSourceScanner against source tree, aggregate into ComplianceReportGenerator, confirm disclaimer survives in report
Wire format: CryptoBOM and markdown report
Security notes: Mandatory SR-15 end-to-end confirmation spanning quantx-compliance
"""

from __future__ import annotations

from pathlib import Path

from quantx_compliance.compliance_report_generator import ComplianceReportGenerator
from quantx_compliance.crypto_bom_model import STATIC_SCANNER_DISCLAIMER
from quantx_compliance.scanners.static_source_scanner import StaticSourceScanner


def test_sr_15_end_to_end_scanner_disclaimer_survives_into_final_report(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    code_file = src_dir / "app.py"
    code_file.write_text("cipher = 'aes-256-gcm'\n", encoding="utf-8")

    # 1. Run static source scan
    scanner = StaticSourceScanner()
    bom = scanner.scan(src_dir)
    assert bom.disclaimer == STATIC_SCANNER_DISCLAIMER

    # 2. Feed BOM into report generator
    generator = ComplianceReportGenerator()
    report = generator.generate(bom)

    # 3. Confirm disclaimer is strictly preserved on the report object and rendered markdown output (SR-15)
    assert report.disclaimer == STATIC_SCANNER_DISCLAIMER
    markdown = report.render_markdown()
    assert STATIC_SCANNER_DISCLAIMER in markdown
    assert "best-effort" in markdown.lower()
    assert "false positive" in markdown.lower()
