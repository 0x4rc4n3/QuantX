# QuantX — Authentication & Authorization Model

**Status:** Pre-implementation · **Note:** this doc covers two different things that are easy to conflate for an auth *product*: (1) the auth model QuantX **exposes** to whoever it's authenticating, and (2) who is authorized to **operate/configure** QuantX itself. Both matter; they're kept separate below.

## 1. The auth model QuantX exposes (subject-facing)

- **Identity:** a `subject_id` — QuantX has no concept of a user profile, email, or password. Identity binding (subject_id → real-world identity) is entirely the integrating application's responsibility.
- **Primary factor:** a signature or KEM-derived proof, verified under a `required_mode` set server-side (hybrid by default; D2). The subject never gets to declare or downgrade the mode (SR-1).
- **Step-up / second factor:** TOTP/HOTP, optionally push. Configured as an additional required gate in `SessionOrchestrator`, not a replacement path.
- **Session:** a token minted only after every configured gate passes (`factors_completed` fully populated — SR-10), validated via `ReplayStore` + `RateLimiter` on every use.
- **Recovery:** backup codes, single-use, tracked the same way as any other replay-sensitive credential.
- **Step-up governance:** for actions above a policy threshold, N-of-M approval via `ThresholdManager`, layered on top of the same underlying `SignatureCombiner` — not a parallel auth system.

This is intentionally minimal — QuantX is an authentication *primitive provider*, not an identity provider (IdP) or a role/permission engine for the client's application. Authorization decisions ("can this subject do X") are the integrating application's business logic; QuantX answers "is this really who/what it claims to be," nothing more.

## 2. Who's authorized to operate/configure QuantX itself

| Role | Can do | Cannot do |
|---|---|---|
| **Integrator** | Wire components, choose a recipe, write client-application authorization logic on top | Sign a production `AlgorithmRegistry` config without holding the signing key |
| **Admin (client-side operator)** | Own the `AlgorithmRegistry` signing key, define registry roles and `required_mode` per role, choose key-custody backend | Bypass `GATE_REVIEW_REQUIRED` sign-off to call something production-ready |
| **Reviewer** | Review and sign off `GATE_REVIEW_REQUIRED` components (`10-security-requirements.md`), log sign-off in `docs/adr/`, run Layer 10 compliance scans | Approve their own authored component (independence is the point of the gate) |
| **Approver (governance)** | Hold one of the N keys in a `ThresholdPolicy`, contribute one signature toward quorum | Count twice — duplicate keys are rejected at policy-creation time (SR-12) |
| **Consulting operator (you)** | Compose any of the above differently per client engagement (D3) | — |

## Registry-level authorization (`AlgorithmRegistry`)

This is the closest thing QuantX has to a config-level "authorization" surface, and it's worth being explicit:

- Dev/demo: `allow_unsigned=True` — anyone with filesystem access to the YAML can change the registry. Fine for Recipe A, never acceptable for Recipe B.
- Production (Recipe B/C): config must be signed; loading rejects unsigned config outright. Whoever holds the signing key is, functionally, the only party who can change what `required_mode` means for a given role.

## Service-to-service authorization (REST sidecar)

Covered in full in `08-api-specification.md`. Summary: the sidecar's *caller* authenticates via bearer token or mTLS — this is authorization for "who may ask QuantX to run a challenge/verify cycle," a distinct concern from the subject-facing auth model in §1 above.

## What this doc deliberately does not attempt

- A generic RBAC/ABAC engine for client applications — out of scope by design; QuantX answers identity questions, not permission questions.
- Multi-tenant role scoping (e.g. "Admin for org A but not org B") — doesn't apply under the per-client composition model; see `11-multi-tenancy-model.md`.
