"""Unit tests for StandardsCatalog lookups and reference sets.

Layer: 10
Depends on: quantx_compliance.standards_catalog.StandardsCatalog, quantx_compliance.standards_catalog.StandardReference
Implements: Pytest tests validating algorithm-to-standard mapping accuracy
Outside: Scanning and report formatting
Inside: Static lookup table querying, standard support verification, and edge case handling
Wire format: In-memory test objects
Security notes: Verifies correct compliance standards association without dynamic remote fetching
"""

from __future__ import annotations

from quantx_compliance.crypto_bom_model import CryptoBOMFinding
from quantx_compliance.standards_catalog import StandardsCatalog
from quantx_core.types.algorithm_id import AlgorithmId


def test_standards_catalog_lookup_known_algorithms(
    sample_standards_catalog: StandardsCatalog,
) -> None:
    # Post-quantum ML-KEM should map to FIPS-203
    ml_kem_refs = sample_standards_catalog.lookup(AlgorithmId.ML_KEM_768)
    assert any(ref.standard_id == "FIPS-203" for ref in ml_kem_refs)

    # Post-quantum ML-DSA should map to FIPS-204
    ml_dsa_refs = sample_standards_catalog.lookup(AlgorithmId.ML_DSA_65)
    assert any(ref.standard_id == "FIPS-204" for ref in ml_dsa_refs)

    # X25519 should map to RFC-7748
    x25519_refs = sample_standards_catalog.lookup(AlgorithmId.X25519)
    assert any(ref.standard_id == "RFC-7748" for ref in x25519_refs)

    # AES should map to FIPS-197
    aes_refs = sample_standards_catalog.lookup("aes-256-gcm")
    assert any(ref.standard_id == "FIPS-197" for ref in aes_refs)


def test_standards_catalog_lookup_from_finding(sample_standards_catalog: StandardsCatalog) -> None:
    finding = CryptoBOMFinding(
        finding_id="f-1",
        source="static_scan",
        algorithm=AlgorithmId.ML_DSA_87,
        location="src/test.py:1",
    )
    refs = sample_standards_catalog.lookup(finding)
    assert len(refs) > 0
    assert any(r.standard_id == "FIPS-204" for r in refs)


def test_standards_catalog_unknown_algorithm_returns_empty(
    sample_standards_catalog: StandardsCatalog,
) -> None:
    refs = sample_standards_catalog.lookup("unknown-experimental-cipher")
    assert refs == []


def test_standards_catalog_has_standard(sample_standards_catalog: StandardsCatalog) -> None:
    assert sample_standards_catalog.has_standard("FIPS-203")
    assert sample_standards_catalog.has_standard("fips-204")
    assert not sample_standards_catalog.has_standard("NON-EXISTENT-STD-999")
