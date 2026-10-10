"""Unit tests for verify router.

Layer: sidecar
Depends on: quantx_service.routers.verify_router, starlette.testclient.TestClient
Implements: Pytest tests verifying POST /v1/verify for genuine response, invalid signature, and replay
Outside: Cryptographic algorithm details
Inside: End-to-end HTTP challenge and response verification, status codes, and error envelopes
Security notes: Verifies genuine responses succeed, invalid signatures yield 401, and replayed challenges yield 409 already_consumed.
"""

from __future__ import annotations

import base64

from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import build_signed_payload
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from starlette.testclient import TestClient


def test_verify_success(client: TestClient, auth_keys: tuple[bytes, bytes, bytes, bytes]) -> None:
    """A genuine signed response against a real challenge returns 200 with session_token."""
    ed_priv, _, mldsa_priv, _ = auth_keys

    # 1. Issue challenge
    resp_chal = client.post("/v1/challenges", json={"subject_id": "alice@quantx.internal"})
    assert resp_chal.status_code == 200
    chal_data = resp_chal.json()
    challenge_id = chal_data["challenge_id"]
    nonce_bytes = base64.b64decode(chal_data["nonce"])

    # 2. Sign canonical challenge nonce
    ed_signer = Ed25519Adapter(private_key=ed_priv)
    mldsa_signer = MlDsa65Adapter(private_key=mldsa_priv)

    payload = build_signed_payload(
        mode=Mode.HYBRID,
        role_id="session-auth",
        message=nonce_bytes,
    )
    ed_sig = ed_signer.sign(payload)
    mldsa_sig = mldsa_signer.sign(payload)

    wire_sig = signature_wire_format.encode(
        Mode.HYBRID,
        [("ed25519", ed_sig), ("ml-dsa-65", mldsa_sig)],
    )
    sig_b64 = base64.b64encode(wire_sig).decode("ascii")

    # 3. Verify
    resp_ver = client.post(
        "/v1/verify",
        json={
            "challenge_id": challenge_id,
            "signature": sig_b64,
        },
    )
    assert resp_ver.status_code == 200
    ver_data = resp_ver.json()
    assert "session_token" in ver_data
    assert ver_data["session_token"].startswith("tok_")
    assert "expires_at" in ver_data


def test_verify_invalid_signature(client: TestClient) -> None:
    """An invalid signature returns 401 verification_failed."""
    resp_chal = client.post("/v1/challenges", json={"subject_id": "bob@quantx.internal"})
    assert resp_chal.status_code == 200
    challenge_id = resp_chal.json()["challenge_id"]

    # Bogus signature
    bogus_sig_b64 = base64.b64encode(b"invalid_signature_bytes_1234567890").decode("ascii")
    resp_ver = client.post(
        "/v1/verify",
        json={
            "challenge_id": challenge_id,
            "signature": bogus_sig_b64,
        },
    )
    assert resp_ver.status_code == 401
    err_data = resp_ver.json()
    assert "error" in err_data
    assert err_data["error"]["code"] == "verification_failed"


def test_verify_replay_rejected(
    client: TestClient, auth_keys: tuple[bytes, bytes, bytes, bytes]
) -> None:
    """A replayed challenge returns 409 already_consumed."""
    ed_priv, _, mldsa_priv, _ = auth_keys

    resp_chal = client.post("/v1/challenges", json={"subject_id": "charlie@quantx.internal"})
    chal_data = resp_chal.json()
    challenge_id = chal_data["challenge_id"]
    nonce_bytes = base64.b64decode(chal_data["nonce"])

    ed_signer = Ed25519Adapter(private_key=ed_priv)
    mldsa_signer = MlDsa65Adapter(private_key=mldsa_priv)

    payload = build_signed_payload(
        mode=Mode.HYBRID,
        role_id="session-auth",
        message=nonce_bytes,
    )
    wire_sig = signature_wire_format.encode(
        Mode.HYBRID,
        [("ed25519", ed_signer.sign(payload)), ("ml-dsa-65", mldsa_signer.sign(payload))],
    )
    sig_b64 = base64.b64encode(wire_sig).decode("ascii")

    # First attempt: succeeds
    resp1 = client.post("/v1/verify", json={"challenge_id": challenge_id, "signature": sig_b64})
    assert resp1.status_code == 200

    # Second attempt: replay rejection (409 already_consumed)
    resp2 = client.post("/v1/verify", json={"challenge_id": challenge_id, "signature": sig_b64})
    assert resp2.status_code == 409
    err_data = resp2.json()
    assert "error" in err_data
    assert err_data["error"]["code"] == "already_consumed"
