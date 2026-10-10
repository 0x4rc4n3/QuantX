"""Security tests for SR-15: Scanner disclaimer attached to all outputs.

Layer: 10
Depends on: quantx_compliance.scanners.static_source_scanner.StaticSourceScanner, quantx_compliance.crypto_bom_model.STATIC_SCANNER_DISCLAIMER
Implements: Mandatory security test for SR-15 (static scanner disclaimer attached to output)
Outside: Detection accuracy heuristics
Inside: Verification that the best-effort/false-positive disclaimer is permanently attached to all scanner outputs
Wire format: In-memory test objects
Security notes: Mandatory SR-15 test. Static scan findings must always carry the best-effort disclaimer.
"""

from __future__ import annotations

from pathlib import Path

from quantx_compliance.crypto_bom_model import STATIC_SCANNER_DISCLAIMER
from quantx_compliance.scanners.static_source_scanner import StaticSourceScanner


def test_sr_15_disclaimer_attached_when_findings_present(temp_source_tree: Path) -> None:
    scanner = StaticSourceScanner()
    bom = scanner.scan(temp_source_tree)

    # 1. Output CryptoBOM must carry the disclaimer
    assert bom.disclaimer is not None
    assert bom.disclaimer == STATIC_SCANNER_DISCLAIMER
    assert "best-effort" in bom.disclaimer.lower()
    assert "false positive" in bom.disclaimer.lower()

    # 2. Every individual finding must carry the disclaimer attached at the finding level
    assert len(bom.findings) > 0
    for finding in bom.findings:
        assert finding.disclaimer is not None
        assert finding.disclaimer == STATIC_SCANNER_DISCLAIMER


def test_sr_15_disclaimer_attached_even_when_zero_findings(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty_repo"
    empty_dir.mkdir()

    scanner = StaticSourceScanner()
    bom = scanner.scan(empty_dir)

    # Must carry disclaimer even when zero findings are produced (SR-15)
    assert len(bom.findings) == 0
    assert bom.disclaimer is not None
    assert bom.disclaimer == STATIC_SCANNER_DISCLAIMER


def test_sr_15_disclaimer_serialized_in_dict_representation(temp_source_tree: Path) -> None:
    scanner = StaticSourceScanner()
    bom = scanner.scan(temp_source_tree)
    exported = bom.to_dict()

    assert "disclaimer" in exported
    assert exported["disclaimer"] == STATIC_SCANNER_DISCLAIMER
    for finding_dict in exported["findings"]:
        assert "disclaimer" in finding_dict
        assert finding_dict["disclaimer"] == STATIC_SCANNER_DISCLAIMER
