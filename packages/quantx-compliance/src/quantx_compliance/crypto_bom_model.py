"""Crypto bill-of-materials (CryptoBOM) data model.

Layer: 10
Depends on: quantx_core.types.algorithm_id.AlgorithmId
Implements: CryptoBOM and CryptoBOMFinding data structures
Outside: Scanning logic (scanners/) and report generation (compliance_report_generator.py)
Inside: Value objects for CryptoBOM findings and collections with trust and disclaimer metadata
Wire format: Native Python dataclasses / dict mappings
Security notes: Preserves trust level ('verified' vs 'unverified') and SR-15 disclaimer per finding and collection
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Iterator

from quantx_core.types.algorithm_id import AlgorithmId

STATIC_SCANNER_DISCLAIMER: str = (
    "DISCLAIMER: Static source scan findings are best-effort heuristics "
    "subject to false positives and false negatives. This scan does not "
    "constitute an exhaustive or authoritative cryptographic audit."
)


@dataclass(frozen=True)
class CryptoBOMFinding:
    """A single finding representing a detected cryptographic primitive/algorithm."""

    finding_id: str
    source: str  # 'static_scan' | 'tls_inspect' | other
    algorithm: AlgorithmId | str
    key_size: int | None = None
    location: str = ""
    trust: str = "verified"  # 'verified' | 'unverified' (SR-13)
    disclaimer: str | None = None  # Attached per SR-15
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alg_str = (
            self.algorithm.value if isinstance(self.algorithm, AlgorithmId) else str(self.algorithm)
        )
        return {
            "finding_id": self.finding_id,
            "source": self.source,
            "algorithm": alg_str,
            "key_size": self.key_size,
            "location": self.location,
            "trust": self.trust,
            "disclaimer": self.disclaimer,
            "metadata": dict(self.metadata),
        }


@dataclass
class CryptoBOM:
    """A collection of cryptographic findings forming a bill of materials."""

    findings: list[CryptoBOMFinding] = field(default_factory=list)
    disclaimer: str | None = None

    def add_finding(self, finding: CryptoBOMFinding) -> None:
        self.findings.append(finding)

    def filter_by_trust(self, trust: str) -> list[CryptoBOMFinding]:
        return [f for f in self.findings if f.trust == trust]

    def filter_by_source(self, source: str) -> list[CryptoBOMFinding]:
        return [f for f in self.findings if f.source == source]

    def to_dict(self) -> dict[str, Any]:
        return {
            "disclaimer": self.disclaimer,
            "findings": [f.to_dict() for f in self.findings],
        }

    def __iter__(self) -> Iterator[CryptoBOMFinding]:
        return iter(self.findings)

    def __len__(self) -> int:
        return len(self.findings)


def make_finding_id() -> str:
    """Generate a unique finding identifier."""
    return str(uuid.uuid4())
