"""Compliance report generator aggregating CryptoBOM findings and standards lookups.

Layer: 10
Depends on: quantx_compliance.crypto_bom_model.CryptoBOM, quantx_compliance.crypto_bom_model.CryptoBOMFinding, quantx_compliance.standards_catalog.StandardsCatalog, quantx_compliance.standards_catalog.StandardReference
Implements: ComplianceReportGenerator.generate(bom, target_standards=None) -> ComplianceReport
Outside: Scanning source trees or TLS endpoints (scanners/); standards reference data definitions (standards_catalog.py)
Inside: Pure aggregation and formatting layer synthesizing CryptoBOM findings with StandardsCatalog references
Wire format: ComplianceReport dataclass with rendered markdown / structured dict
Security notes: Enforces FR-10.4 (no invented facts, pure aggregation); preserves SR-13 trust tags and SR-15 disclaimers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantx_compliance.crypto_bom_model import CryptoBOM, CryptoBOMFinding
from quantx_compliance.standards_catalog import StandardReference, StandardsCatalog


@dataclass(frozen=True)
class EvaluatedFinding:
    """A CryptoBOM finding paired with its associated standards references."""

    finding: CryptoBOMFinding
    standards: list[StandardReference] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding": self.finding.to_dict(),
            "standards": [s.to_dict() for s in self.standards],
        }


@dataclass
class ComplianceReport:
    """Formatted compliance report preserving trust tags, disclaimers, and standards mappings."""

    disclaimer: str | None
    evaluated_findings: list[EvaluatedFinding] = field(default_factory=list)
    unsupported_standards: list[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines: list[str] = ["# QuantX Cryptographic Compliance Report\n"]

        # Prominently attach disclaimer if present (SR-15)
        if self.disclaimer:
            lines.append(f"> [!WARNING]\n> {self.disclaimer}\n")

        # Unsupported / missing standards warnings (edge case from 13-error-and-edge-cases.md)
        if self.unsupported_standards:
            lines.append("## Unrecognized Standards\n")
            for unsup in self.unsupported_standards:
                lines.append(f"- Warning: No data for standard: `{unsup}`")
            lines.append("")

        lines.append("## Findings Summary\n")
        lines.append(f"Total findings: {len(self.evaluated_findings)}\n")

        if not self.evaluated_findings:
            lines.append("No cryptographic algorithms detected.\n")
            return "\n".join(lines)

        lines.append("| Finding ID | Algorithm | Location | Trust Level | Standards |")
        lines.append("|---|---|---|---|---|")
        for entry in self.evaluated_findings:
            f = entry.finding
            stds_str = ", ".join(s.standard_id for s in entry.standards) or "None mapped"
            lines.append(
                f"| `{f.finding_id[:8]}` | `{f.algorithm}` | `{f.location}` | **{f.trust}** | {stds_str} |"
            )

        lines.append("\n## Detailed Findings\n")
        for entry in self.evaluated_findings:
            f = entry.finding
            lines.append(f"### Finding `{f.finding_id}`")
            lines.append(f"- **Source:** {f.source}")
            lines.append(f"- **Algorithm:** {f.algorithm}")
            lines.append(f"- **Key Size:** {f.key_size if f.key_size is not None else 'N/A'}")
            lines.append(f"- **Location:** {f.location}")
            lines.append(f"- **Trust Level:** {f.trust}")
            if f.disclaimer:
                lines.append(f"- **Disclaimer:** {f.disclaimer}")
            if entry.standards:
                lines.append("- **Standards References:**")
                for std in entry.standards:
                    lines.append(f"  - `{std.standard_id}`: {std.title} ({std.status})")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "disclaimer": self.disclaimer,
            "unsupported_standards": list(self.unsupported_standards),
            "findings": [ef.to_dict() for ef in self.evaluated_findings],
        }


class ComplianceReportGenerator:
    """Generates structured compliance reports by aggregating findings with standards catalog."""

    def __init__(self, catalog: StandardsCatalog | None = None) -> None:
        self.catalog = catalog if catalog is not None else StandardsCatalog()

    def generate(
        self,
        bom: CryptoBOM,
        target_standards: list[str] | None = None,
    ) -> ComplianceReport:
        """Generate a compliance report from a CryptoBOM.

        Every fact in the report traces directly to the BOM or StandardsCatalog (FR-10.4).
        Trust-level tags (SR-13) and scanner disclaimers (SR-15) are strictly preserved.
        """
        unsupported: list[str] = []
        if target_standards:
            for std in target_standards:
                if not self.catalog.has_standard(std):
                    unsupported.append(std)

        evaluated: list[EvaluatedFinding] = []
        for finding in bom.findings:
            refs = self.catalog.lookup(finding)
            if target_standards:
                normalized_targets = {s.upper() for s in target_standards}
                refs = [r for r in refs if r.standard_id.upper() in normalized_targets]
            evaluated.append(EvaluatedFinding(finding=finding, standards=refs))

        # Preserve collection disclaimer (e.g. from static scanner)
        report_disclaimer = bom.disclaimer

        return ComplianceReport(
            disclaimer=report_disclaimer,
            evaluated_findings=evaluated,
            unsupported_standards=unsupported,
        )
