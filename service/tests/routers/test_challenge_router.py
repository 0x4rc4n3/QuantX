"""Unit tests for challenge router.

Layer: sidecar
Depends on: quantx_service.routers.challenge_router, starlette.testclient.TestClient
Implements: Pytest tests verifying POST /v1/challenges and error envelopes
Outside: Crytographic primitives and session orchestrator internals
Inside: Validating response shape, required fields, and malformed request handling
Security notes: Confirms nonce and required_mode are returned without trusting client input.
"""

from __future__ import annotations

import base64

from starlette.testclient import TestClient


def test_create_challenge_success(client: TestClient) -> None:
    """A valid challenge request returns 200 with expected schema fields."""
    response = client.post("/v1/challenges", json={"subject_id": "alice@quantx.internal"})
    assert response.status_code == 200
    data = response.json()
    assert "challenge_id" in data
    assert data["challenge_id"].startswith("chal_")
    assert "nonce" in data
    # Nonce must be valid base64
    nonce_bytes = base64.b64decode(data["nonce"])
    assert len(nonce_bytes) > 0
    assert data["required_mode"] == "HYBRID"
    assert "expires_at" in data


def test_create_challenge_malformed_empty_subject(client: TestClient) -> None:
    """An empty subject ID returns 400 malformed_request."""
    response = client.post("/v1/challenges", json={"subject_id": ""})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "malformed_request"


def test_create_challenge_malformed_missing_field(client: TestClient) -> None:
    """A missing subject_id field returns 400 malformed_request."""
    response = client.post("/v1/challenges", json={})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "malformed_request"
