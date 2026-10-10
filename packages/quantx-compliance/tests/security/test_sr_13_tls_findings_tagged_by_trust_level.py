"""Security tests for SR-13: TLS findings tagged by trust level.

Layer: 10
Depends on: quantx_compliance.scanners.tls_inspector.TlsInspector, quantx_compliance.crypto_bom_model.CryptoBOM
Implements: Automated security test for SR-13 (TLS findings tagged 'verified' vs 'unverified')
Outside: General static scanning
Inside: Verification that permissive probe findings are explicitly tagged 'unverified' and authenticated probe fails on untrusted certs
Wire format: In-memory test objects
Security notes: Mandatory SR-13 test. Unauthenticated probes are never presented as equivalent to authenticated ones.
"""

from __future__ import annotations

import datetime
import socket
import ssl
import threading
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from quantx_compliance.crypto_bom_model import CryptoBOM
from quantx_compliance.scanners.tls_inspector import TlsInspector


@pytest.fixture
def ephemeral_self_signed_tls_server(tmp_path: Path):
    """Spins up a local TLS server with a self-signed certificate on an ephemeral port."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "127.0.0.1")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    cert_file = tmp_path / "server_cert.pem"
    key_file = tmp_path / "server_key.pem"
    cert_file.write_bytes(cert_pem)
    key_file.write_bytes(key_pem)

    server_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    server_ctx.load_cert_chain(str(cert_file), str(key_file))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.listen(10)

    stop_event = threading.Event()

    def accept_loop():
        sock.settimeout(0.5)
        while not stop_event.is_set():
            try:
                csock, _ = sock.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            try:
                ssock = server_ctx.wrap_socket(csock, server_side=True)
                ssock.recv(1024)
                ssock.close()
            except Exception:
                pass

    thread = threading.Thread(target=accept_loop, daemon=True)
    thread.start()

    yield ("127.0.0.1", port, cert.public_bytes(serialization.Encoding.DER))

    stop_event.set()
    sock.close()
    thread.join(timeout=1.0)


def test_sr_13_authenticated_probe_fails_on_untrusted_endpoint(
    ephemeral_self_signed_tls_server: tuple[str, int, bytes],
) -> None:
    host, port, _ = ephemeral_self_signed_tls_server
    inspector = TlsInspector(default_timeout=2.0)

    # Authenticated probe (default) against self-signed cert must fail verification
    with pytest.raises((ssl.SSLCertVerificationError, ssl.SSLError)):
        inspector.inspect(endpoint=f"{host}:{port}", mode="authenticated")


def test_sr_13_permissive_probe_findings_are_tagged_unverified(
    ephemeral_self_signed_tls_server: tuple[str, int, bytes],
) -> None:
    host, port, _ = ephemeral_self_signed_tls_server
    inspector = TlsInspector(default_timeout=2.0)

    # Opt-in permissive probe succeeds, but findings are strictly tagged 'unverified'
    bom = inspector.inspect(endpoint=f"{host}:{port}", mode="permissive")
    assert len(bom.findings) > 0
    for finding in bom.findings:
        assert (
            finding.trust == "unverified"
        ), "Permissive probe must tag findings as 'unverified' (SR-13)"


def test_sr_13_findings_never_merged_untagged(mock_rsa_cert_der: bytes) -> None:
    inspector = TlsInspector()

    # Authenticated / verified finding
    verified_bom = inspector.parse_certificate_der(
        mock_rsa_cert_der,
        location="auth.corp.com:443",
        trust="verified",
    )
    # Permissive / unverified finding
    unverified_bom = inspector.parse_certificate_der(
        mock_rsa_cert_der,
        location="unverified.dev:443",
        trust="unverified",
    )

    combined_bom = CryptoBOM()
    for f in verified_bom.findings:
        combined_bom.add_finding(f)
    for f in unverified_bom.findings:
        combined_bom.add_finding(f)

    # Verify that every finding has an explicit trust tag ('verified' or 'unverified')
    for finding in combined_bom.findings:
        assert finding.trust in ("verified", "unverified")
        assert finding.trust != ""

    verified_findings = combined_bom.filter_by_trust("verified")
    unverified_findings = combined_bom.filter_by_trust("unverified")

    assert len(verified_findings) == 1
    assert len(unverified_findings) == 1
    assert verified_findings[0].location == "auth.corp.com:443"
    assert unverified_findings[0].location == "unverified.dev:443"
