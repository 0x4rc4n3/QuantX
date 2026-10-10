"""Security test: SR-1 sidecar boundary never trusts declared mode.

Layer: sidecar
Depends on: quantx_service.routers.verify_router, starlette.testclient.TestClient
Implements: Mandatory automated security test for SR-1 at the sidecar boundary
Outside: Library-level combiner mode tests
Inside: HTTP-level mode-override and downgrade attempts against POST /v1/verify
Security notes: Confirms that attempting to declare CLASSICAL_ONLY or smuggle mode overrides on the wire fails closed with 401 verification_failed.
"""

from __future__ import annotations

import base64

from quantx_combiners.signature import signature_wire_format
from quantx_combiners.signature.signature_combiner import build_signed_payload
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from starlette.testclient import TestClient


def test_sr_01_sidecar_rejects_declared_mode_downgrade(
    client: TestClient,
    auth_keys: tuple[bytes, bytes, bytes, bytes],
) -> None:
    """SR-1 (sidecar): Client attempting to declare CLASSICAL_ONLY against a HYBRID challenge is rejected."""
    ed_priv, _, _, _ = auth_keys

    # 1. Server issues a HYBRID challenge
    resp_chal = client.post("/v1/challenges", json={"subject_id": "eve@quantx.internal"})
    assert resp_chal.status_code == 200
    chal_data = resp_chal.json()
    challenge_id = chal_data["challenge_id"]
    nonce_bytes = base64.b64decode(chal_data["nonce"])

    # 2. Attacker strips PQC component, signs classical only, declares CLASSICAL_ONLY
    ed_signer = Ed25519Adapter(private_key=ed_priv)
    payload = build_signed_payload(
        mode=Mode.CLASSICAL_ONLY, role_id="session-auth", message=nonce_bytes
    )
    ed_sig = ed_signer.sign(payload)

    wire_sig = signature_wire_format.encode(Mode.CLASSICAL_ONLY, [("ed25519", ed_sig)])
    sig_b64 = base64.b64encode(wire_sig).decode("ascii")

    # 3. Post to /verify with declared_mode: "CLASSICAL_ONLY"
    resp_ver = client.post(
        "/v1/verify",
        json={
            "challenge_id": challenge_id,
            "signature": sig_b64,
            "declared_mode": "CLASSICAL_ONLY",
        },
    )
    # Must reject with 401 verification_failed
    assert resp_ver.status_code == 401
    err_data = resp_ver.json()
    assert "error" in err_data
    assert err_data["error"]["code"] == "verification_failed"


def test_sr_01_sidecar_rejects_mode_mismatch_even_if_signature_hybrid(
    client: TestClient,
    auth_keys: tuple[bytes, bytes, bytes, bytes],
) -> None:
    """SR-1 (sidecar): Request body declaring an incompatible mode is rejected unconditionally."""
    ed_priv, _, mldsa_priv, _ = auth_keys

    resp_chal = client.post("/v1/challenges", json={"subject_id": "eve2@quantx.internal"})
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

    # Claim PQC_ONLY when server role requires HYBRID
    resp_ver = client.post(
        "/v1/verify",
        json={
            "challenge_id": challenge_id,
            "signature": sig_b64,
            "declared_mode": "PQC_ONLY",
        },
    )
    assert resp_ver.status_code == 401
    assert resp_ver.json()["error"]["code"] == "verification_failed"
