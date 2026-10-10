"""Unit tests for CryptoBOM and CryptoBOMFinding data structures.

Layer: 10
Depends on: quantx_compliance.crypto_bom_model.CryptoBOM, quantx_compliance.crypto_bom_model.CryptoBOMFinding
Implements: Pytest test functions verifying CryptoBOM model shape and properties
Outside: Scanner behavior and network I/O
Inside: CryptoBOM model instantiation, filtering by trust level and source, and serialization
Wire format: In-memory test objects
Security notes: Verifies that trust-level tags and SR-15 disclaimers are preserved in data structures
"""

from __future__ import annotations

from quantx_compliance.crypto_bom_model import (
    STATIC_SCANNER_DISCLAIMER,
    CryptoBOM,
    CryptoBOMFinding,
)
from quantx_core.types.algorithm_id import AlgorithmId


def test_crypto_bom_finding_creation_and_attributes() -> None:
    finding = CryptoBOMFinding(
        finding_id="test-1",
        source="static_scan",
        algorithm=AlgorithmId.ML_KEM_768,
        key_size=None,
        location="path/to/code.py:10",
        trust="unverified",
        disclaimer=STATIC_SCANNER_DISCLAIMER,
        metadata={"extra": "data"},
    )

    assert finding.finding_id == "test-1"
    assert finding.source == "static_scan"
    assert finding.algorithm == AlgorithmId.ML_KEM_768
    assert finding.trust == "unverified"
    assert finding.disclaimer == STATIC_SCANNER_DISCLAIMER
    assert finding.metadata["extra"] == "data"

    data = finding.to_dict()
    assert data["finding_id"] == "test-1"
    assert data["algorithm"] == "ml-kem-768"
    assert data["trust"] == "unverified"
    assert data["disclaimer"] == STATIC_SCANNER_DISCLAIMER


def test_crypto_bom_collection_operations(sample_crypto_bom: CryptoBOM) -> None:
    assert len(sample_crypto_bom) == 3

    verified = sample_crypto_bom.filter_by_trust("verified")
    assert len(verified) == 1
    assert verified[0].finding_id == "find-002"

    unverified = sample_crypto_bom.filter_by_trust("unverified")
    assert len(unverified) == 2

    static_findings = sample_crypto_bom.filter_by_source("static_scan")
    assert len(static_findings) == 1
    assert static_findings[0].finding_id == "find-001"

    tls_findings = sample_crypto_bom.filter_by_source("tls_inspect")
    assert len(tls_findings) == 2


def test_crypto_bom_to_dict_preserves_disclaimer_and_findings(sample_crypto_bom: CryptoBOM) -> None:
    exported = sample_crypto_bom.to_dict()
    assert exported["disclaimer"] == STATIC_SCANNER_DISCLAIMER
    assert len(exported["findings"]) == 3
    assert exported["findings"][0]["finding_id"] == "find-001"
