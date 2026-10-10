"""TLS endpoint inspector and leaf certificate parser.

Layer: 10
Depends on: quantx_compliance.crypto_bom_model.CryptoBOM, quantx_compliance.crypto_bom_model.CryptoBOMFinding, quantx_compliance.crypto_bom_model.make_finding_id, cryptography.x509
Implements: TlsInspector.inspect(endpoint, mode='authenticated', port=443, timeout=5.0) -> CryptoBOM
Outside: Static source code scanning (static_source_scanner.py); report generation (compliance_report_generator.py)
Inside: TLS socket probing and in-process leaf certificate parsing via cryptography.x509.load_der_x509_certificate
Wire format: DER bytes in, CryptoBOM out
Security notes: Enforces SR-13 (permissive findings tagged 'unverified', authenticated tagged 'verified') and FR-10.3 (in-process x509 parsing, no openssl subprocess shell-out)
"""

from __future__ import annotations

import socket
import ssl
from typing import Any
from urllib.parse import urlparse

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, ed448, ed25519, rsa, x25519

from quantx_compliance.crypto_bom_model import (
    CryptoBOM,
    CryptoBOMFinding,
    make_finding_id,
)


class TlsInspector:
    """Probes TLS endpoints and parses leaf certificates using cryptography.x509."""

    def __init__(self, default_timeout: float = 5.0) -> None:
        self.default_timeout = default_timeout

    def _parse_endpoint(self, endpoint: str, default_port: int = 443) -> tuple[str, int]:
        """Extract host and port from endpoint string or URL."""
        if "://" in endpoint:
            parsed = urlparse(endpoint)
            host = parsed.hostname or endpoint
            port = parsed.port or default_port
        elif ":" in endpoint:
            parts = endpoint.split(":", 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                port = default_port
        else:
            host = endpoint
            port = default_port
        return host, port

    def inspect(
        self,
        endpoint: str,
        mode: str = "authenticated",
        port: int | None = None,
        timeout: float | None = None,
    ) -> CryptoBOM:
        """Probe a TLS endpoint and return a CryptoBOM with findings tagged by trust level.

        Args:
            endpoint: Hostname, IP, or URL to inspect.
            mode: 'authenticated' (default, validates cert and hostname) or
                  'permissive' (explicit opt-in, CERT_NONE).
            port: Port override.
            timeout: Socket connection timeout in seconds.

        Returns:
            CryptoBOM with leaf certificate findings. Findings from permissive probes
            are tagged with trust='unverified' (SR-13).
        """
        if mode not in ("authenticated", "permissive"):
            raise ValueError(f"Invalid mode '{mode}'. Must be 'authenticated' or 'permissive'.")

        host, resolved_port = self._parse_endpoint(endpoint, port or 443)
        effective_port = port if port is not None else resolved_port
        effective_timeout = timeout if timeout is not None else self.default_timeout

        if mode == "authenticated":
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            trust = "verified"
        else:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            trust = "unverified"

        with socket.create_connection(
            (host, effective_port), timeout=effective_timeout
        ) as raw_sock:
            with context.wrap_socket(raw_sock, server_hostname=host) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                if not der_cert:
                    raise ValueError(f"No peer certificate returned by {host}:{effective_port}")
                tls_version = ssock.version()
                cipher = ssock.cipher()

        location = f"{host}:{effective_port}"
        return self.parse_certificate_der(
            der_bytes=der_cert,
            location=location,
            trust=trust,
            metadata={
                "probe_mode": mode,
                "tls_version": tls_version,
                "cipher_suite": cipher[0] if cipher else None,
            },
        )

    def parse_certificate_der(
        self,
        der_bytes: bytes,
        location: str = "certificate",
        trust: str = "verified",
        metadata: dict[str, Any] | None = None,
    ) -> CryptoBOM:
        """Parse raw DER x509 certificate using cryptography (FR-10.3, no openssl shell-out)."""
        cert = x509.load_der_x509_certificate(der_bytes)
        bom = CryptoBOM()

        # Extract signature algorithm
        sig_oid = cert.signature_algorithm_oid
        sig_alg_name = sig_oid._name or sig_oid.dotted_string

        # Extract public key and key size
        pub_key = cert.public_key()
        key_size: int | None = None
        if isinstance(pub_key, rsa.RSAPublicKey):
            key_size = pub_key.key_size
        elif isinstance(pub_key, ec.EllipticCurvePublicKey):
            key_size = pub_key.key_size
        elif isinstance(pub_key, (ed25519.Ed25519PublicKey, x25519.X25519PublicKey)):
            key_size = 256
        elif isinstance(pub_key, ed448.Ed448PublicKey):
            key_size = 448
        elif hasattr(pub_key, "key_size"):
            key_size = getattr(pub_key, "key_size")

        finding_meta = dict(metadata or {})
        try:
            finding_meta["subject"] = cert.subject.rfc4514_string()
            finding_meta["issuer"] = cert.issuer.rfc4514_string()
            finding_meta["serial_number"] = str(cert.serial_number)
        except Exception:
            pass

        finding = CryptoBOMFinding(
            finding_id=make_finding_id(),
            source="tls_inspect",
            algorithm=sig_alg_name,
            key_size=key_size,
            location=location,
            trust=trust,
            disclaimer=None,
            metadata=finding_meta,
        )
        bom.add_finding(finding)
        return bom
