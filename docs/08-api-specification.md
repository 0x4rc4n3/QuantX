# QuantX — API Specification (REST Sidecar)

**Status:** Pre-implementation, written ahead of the sidecar's own build step · **Depends on:** Layer 4 (`ChallengeIssuer`, `SessionOrchestrator`) for the semantics being exposed

## Why this exists now

Written at design time so the contract is settled before the sidecar is built — the sidecar goes up as soon as Layer 4 is done (`02-build-order.md`), gaining surface as later layers land. Treat every field here as a design decision to validate once it's built, not as already-shipped.

## Scope

The REST sidecar fronts `SessionOrchestrator` for consumers who don't want the Python SDK directly (a client's non-Python service, a quick integration test, etc.). It does **not** expose Layer 8/9/10 by default — those stay SDK-only unless a specific client engagement calls for exposing them too.

## Transport & auth

- HTTPS only, terminated with a hybrid TLS 1.3 key-exchange group (e.g. X25519MLKEM768) — no plaintext HTTP endpoint, including in dev, and the sidecar's own transport doesn't get to be the classical-only weak link in a PQC-migration product (`06-system-architecture.md`).
- Service-to-service authentication (the sidecar's own caller, not the end subject) is a bearer token or mTLS client cert — either is acceptable, plaintext shared secret in a query string is not.
- The sidecar does not itself decide `required_mode` — that's still the `AlgorithmRegistry`'s job underneath. The sidecar is a transport, not a policy layer.

## Endpoints

### `POST /challenge`

Request:
```json
{ "subject_id": "string" }
```

Response `200`:
```json
{
  "challenge_id": "string",
  "nonce": "base64",
  "expires_at": "ISO-8601"
}
```

Note: `required_mode` is **not** returned to the caller as something they can echo back to change behavior — it's enforced server-side regardless of what's sent to `/verify` (SR-1, same as the SDK-level guarantee).

### `POST /verify`

Request:
```json
{
  "challenge_id": "string",
  "signature": "base64",
  "declared_mode": "HYBRID | PQC_ONLY | CLASSICAL_ONLY"
}
```

`declared_mode` here is used only to parse the signature bytes' shape — it is cross-checked against the server's `required_mode` before any verification runs, and a mismatch rejects unconditionally, mirroring FR-2.3 exactly.

Response `200` (success):
```json
{ "session_token": "string", "expires_at": "ISO-8601" }
```

Response `401` (failure — covers bad signature, downgrade attempt, replay, and rate-limit in one status code; see error model below for how to tell them apart).

### `GET /session/:id`

Response `200`:
```json
{ "valid": true, "subject_id": "string", "factors_completed": ["primary", "totp"] }
```

Response `404` if the token doesn't exist or has expired.

## Error model

All error responses share one envelope:

```json
{ "error": { "code": "string", "message": "string" } }
```

| HTTP | `code` | Meaning |
|---|---|---|
| 400 | `malformed_request` | Missing/invalid field, unparseable signature bytes |
| 401 | `verification_failed` | Signature invalid, or mode mismatch (downgrade attempt) — deliberately not distinguished in the response body, to avoid giving an attacker an oracle |
| 404 | `not_found` | Unknown/expired challenge or session |
| 409 | `already_consumed` | Replay of a challenge, token, backup code, or push approval |
| 429 | `rate_limited` | Per-identity or global limiter tripped; `Retry-After` header set |
| 503 | `backend_unavailable` | Underlying `KeyValueStore`/custody backend unreachable — surfaces SR-4/SR-6-class backend failures rather than hiding them as a generic 500 |

Deliberately conflating `verification_failed` reasons (bad signature vs. downgrade attempt) in the response body is intentional — the internal mandatory test suite (`10-security-requirements.md`) still distinguishes them precisely; the wire response does not, so as not to hand an attacker a distinguishing oracle.

## Versioning

Path-prefixed from the start: `/v1/challenge`, `/v1/verify`, `/v1/session/:id`. No unversioned endpoint ships, even for `v1` — this avoids an implicit-versioning migration later.

## Rate limiting on the wire

`429` responses carry `Retry-After`. The limiter itself is the same Layer 0 `RateLimiter` the SDK uses — the sidecar doesn't reimplement rate-limiting policy, it just surfaces it over HTTP.

## Explicitly out of scope for this API

- No endpoint for Layer 5 TOTP enrollment/QR-code generation — that stays a client-application concern; the sidecar only verifies, via `/verify` once TOTP is wired into the underlying `SessionOrchestrator`.
- No admin/config endpoints (registry management, key rotation) — those remain SDK/CLI-level operator actions, not exposed over the network surface by default.
- No multi-tenant routing (`/org/:id/challenge` etc.) — see `11-multi-tenancy-model.md` for why; each sidecar deployment serves one composed configuration.
