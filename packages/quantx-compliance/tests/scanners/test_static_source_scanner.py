"""Unit tests for StaticSourceScanner detection accuracy on sample source trees.

Layer: 10
Depends on: quantx_compliance.scanners.static_source_scanner.StaticSourceScanner, pathlib.Path
Implements: Pytest tests verifying detection of known cryptographic patterns in source files
Outside: Network/TLS inspection and SR-15 disclaimer isolation check
Inside: Source file scanning, pattern matching accuracy, and finding generation
Wire format: In-memory test objects
Security notes: Verifies detection accuracy of static scanning heuristics on sample codebase
"""

from __future__ import annotations

from pathlib import Path

from quantx_compliance.scanners.static_source_scanner import StaticSourceScanner


def test_static_source_scanner_detects_known_patterns(temp_source_tree: Path) -> None:
    scanner = StaticSourceScanner()
    bom = scanner.scan(temp_source_tree)

    assert len(bom.findings) > 0
    algs_found = {f.algorithm for f in bom.findings}

    # Should detect ML-KEM-768, X25519, AES-256-GCM from file1
    assert "ml-kem-768" in algs_found
    assert "x25519" in algs_found
    assert "aes-256-gcm" in algs_found

    # Should detect ML-DSA-65, RSA-2048, SHA-256 from file2
    assert "ml-dsa-65" in algs_found
    assert "rsa-2048" in algs_found
    assert "sha-256" in algs_found

    # Locations should accurately report file path and line number
    for finding in bom.findings:
        assert ":" in finding.location
        assert finding.source == "static_scan"


def test_static_source_scanner_handles_empty_or_non_crypto_tree(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    dummy_file = empty_dir / "plain.py"
    dummy_file.write_text("print('hello world')\n", encoding="utf-8")

    scanner = StaticSourceScanner()
    bom = scanner.scan(empty_dir)

    assert len(bom.findings) == 0
