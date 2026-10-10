"""Static source code scanner for cryptographic algorithm usage.

Layer: 10
Depends on: quantx_compliance.crypto_bom_model.CryptoBOM, quantx_compliance.crypto_bom_model.CryptoBOMFinding, quantx_compliance.crypto_bom_model.STATIC_SCANNER_DISCLAIMER, quantx_compliance.crypto_bom_model.make_finding_id
Implements: StaticSourceScanner.scan(source_paths) -> CryptoBOM
Outside: Network/TLS inspection (tls_inspector.py); report formatting (compliance_report_generator.py)
Inside: Static regex and pattern scanning over source code trees for cryptographic algorithms and primitives
Wire format: In-memory CryptoBOM populated with finding objects
Security notes: Enforces SR-15: attaches permanent best-effort and false-positive/negative disclaimer to every output
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Sequence

from quantx_compliance.crypto_bom_model import (
    STATIC_SCANNER_DISCLAIMER,
    CryptoBOM,
    CryptoBOMFinding,
    make_finding_id,
)

# Known regex patterns mapped to normalized algorithm names and key sizes
_PATTERNS: list[tuple[re.Pattern[str], str, int | None]] = [
    # Post-quantum
    (re.compile(r"\bml[-_]?kem[-_]?768\b", re.IGNORECASE), "ml-kem-768", None),
    (re.compile(r"\bml[-_]?kem[-_]?1024\b", re.IGNORECASE), "ml-kem-1024", None),
    (re.compile(r"\bml[-_]?kem\b", re.IGNORECASE), "ml-kem", None),
    (re.compile(r"\bkyber[-_]?768\b", re.IGNORECASE), "ml-kem-768", None),
    (re.compile(r"\bkyber[-_]?1024\b", re.IGNORECASE), "ml-kem-1024", None),
    (re.compile(r"\bml[-_]?dsa[-_]?65\b", re.IGNORECASE), "ml-dsa-65", None),
    (re.compile(r"\bml[-_]?dsa[-_]?87\b", re.IGNORECASE), "ml-dsa-87", None),
    (re.compile(r"\bml[-_]?dsa\b", re.IGNORECASE), "ml-dsa", None),
    (re.compile(r"\bdilithium[-_]?3\b", re.IGNORECASE), "ml-dsa-65", None),
    (re.compile(r"\bdilithium[-_]?5\b", re.IGNORECASE), "ml-dsa-87", None),
    (re.compile(r"\bslh[-_]?dsa\b", re.IGNORECASE), "slh-dsa", None),
    # Classical asymmetric
    (re.compile(r"\bed25519\b", re.IGNORECASE), "ed25519", 256),
    (re.compile(r"\bx25519\b", re.IGNORECASE), "x25519", 256),
    (re.compile(r"\bcurve25519\b", re.IGNORECASE), "x25519", 256),
    (re.compile(r"\becdsa[-_]p256\b", re.IGNORECASE), "ecdsa-p256", 256),
    (re.compile(r"\bsecp256r1\b", re.IGNORECASE), "ecdsa-p256", 256),
    (re.compile(r"\brsa[-_]?4096\b", re.IGNORECASE), "rsa-4096", 4096),
    (re.compile(r"\brsa[-_]?2048\b", re.IGNORECASE), "rsa-2048", 2048),
    (re.compile(r"\brsa\b", re.IGNORECASE), "rsa", None),
    # Symmetric
    (re.compile(r"\baes[-_]?256[-_]?gcm\b", re.IGNORECASE), "aes-256-gcm", 256),
    (re.compile(r"\baes[-_]?128[-_]?gcm\b", re.IGNORECASE), "aes-128-gcm", 128),
    (re.compile(r"\baes[-_]?gcm\b", re.IGNORECASE), "aes-gcm", None),
    (re.compile(r"\baes\b", re.IGNORECASE), "aes", None),
    # Hashes
    (re.compile(r"\bsha[-_]?256\b", re.IGNORECASE), "sha-256", 256),
    (re.compile(r"\bsha[-_]?512\b", re.IGNORECASE), "sha-512", 512),
    (re.compile(r"\bsha[-_]?1\b", re.IGNORECASE), "sha-1", 160),
    (re.compile(r"\bmd5\b", re.IGNORECASE), "md5", 128),
]

_SUPPORTED_EXTENSIONS = {
    ".py",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".java",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
}


class StaticSourceScanner:
    """Scans source code trees for cryptographic algorithms and primitives."""

    def __init__(self, include_extensions: set[str] | None = None) -> None:
        self.extensions = include_extensions or _SUPPORTED_EXTENSIONS

    def scan(self, source_paths: Sequence[Path | str] | Path | str) -> CryptoBOM:
        """Scan source files or directories for cryptographic usage.

        Returns a CryptoBOM with findings and the permanent SR-15 disclaimer attached.
        """
        bom = CryptoBOM(disclaimer=STATIC_SCANNER_DISCLAIMER)

        paths: list[Path] = []
        if isinstance(source_paths, (str, Path)):
            paths.append(Path(source_paths))
        else:
            for p in source_paths:
                paths.append(Path(p))

        target_files: list[Path] = []
        for p in paths:
            if not p.exists():
                continue
            if p.is_file():
                target_files.append(p)
            elif p.is_dir():
                for root, _, files in os.walk(p):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in self.extensions:
                            target_files.append(file_path)

        for file_path in target_files:
            self._scan_file(file_path, bom)

        return bom

    def _scan_file(self, file_path: Path, bom: CryptoBOM) -> None:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        lines = content.splitlines()
        for line_num, line in enumerate(lines, start=1):
            for regex, alg_name, key_size in _PATTERNS:
                if regex.search(line):
                    finding = CryptoBOMFinding(
                        finding_id=make_finding_id(),
                        source="static_scan",
                        algorithm=alg_name,
                        key_size=key_size,
                        location=f"{file_path}:{line_num}",
                        trust="unverified",  # Static scans are inherently heuristic
                        disclaimer=STATIC_SCANNER_DISCLAIMER,
                        metadata={"matched_line": line.strip()},
                    )
                    bom.add_finding(finding)
