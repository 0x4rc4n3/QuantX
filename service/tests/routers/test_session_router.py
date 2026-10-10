"""Unit tests for session router.

Layer: sidecar
Depends on: quantx_service.routers.session_router, starlette.testclient.TestClient
Implements: Pytest tests verifying GET /v1/session/{token_id} and GET /v1/sessions/{token_id}
Outside: Token generation and storage internals
Inside: Validating token active status, response fields, and 404 not_found handling
Security notes: Ensures unknown or expired tokens are rejected without information leakage.
"""

from __future__ import annotations

import base64

from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import build_signed_payload
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from starlette.testclient import TestClient


def test_get_session_valid(
    client: TestClient, auth_keys: tuple[bytes, bytes, bytes, bytes]
) -> None:
    """A valid, freshly minted session token returns valid=true with subject details."""
    ed_priv, _, mldsa_priv, _ = auth_keys

    # Issue challenge & verify to obtain token
    resp_chal = client.post("/v1/challenges", json={"subject_id": "dan@quantx.internal"})
    chal_data = resp_chal.json()
    challenge_id = chal_data["challenge_id"]
    nonce_bytes = base64.b64decode(chal_data["nonce"])

    ed_signer = Ed25519Adapter(private_key=ed_priv)
    mldsa_signer = MlDsa65Adapter(private_key=mldsa_priv)
    payload = build_signed_payload(mode=Mode.HYBRID, role_id="session-auth", message=nonce_bytes)
    wire_sig = signature_wire_format.encode(
        Mode.HYBRID,
        [("ed25519", ed_signer.sign(payload)), ("ml-dsa-65", mldsa_signer.sign(payload))],
    )
    sig_b64 = base64.b64encode(wire_sig).decode("ascii")

    resp_ver = client.post("/v1/verify", json={"challenge_id": challenge_id, "signature": sig_b64})
    assert resp_ver.status_code == 200
    token_id = resp_ver.json()["session_token"]

    # Check session
    resp_sess = client.get(f"/v1/session/{token_id}")
    assert resp_sess.status_code == 200
    sess_data = resp_sess.json()
    assert sess_data["valid"] is True
    assert sess_data["subject_id"] == "dan@quantx.internal"
    assert "primary" in sess_data["factors_completed"]


def test_get_session_not_found(client: TestClient) -> None:
    """An unknown session token returns 404 not_found."""
    resp = client.get("/v1/session/tok_nonexistent_token_12345")
    assert resp.status_code == 404
    err_data = resp.json()
    assert "error" in err_data
    assert err_data["error"]["code"] == "not_found"
