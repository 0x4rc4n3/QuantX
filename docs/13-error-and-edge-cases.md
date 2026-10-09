# QuantX — Error & Edge-Case Specification

**Status:** Pre-implementation · **Purpose:** so nobody — human or AI assistant — invents inconsistent behavior when they hit a case not spelled out elsewhere. Each row states the required behavior, not just the scenario.

## Wire / input handling

| What happens if... | Required behavior |
|---|---|
| Signature/KEM bytes are malformed or truncated | `verify()` catches the parse failure internally and returns `False` — never raises (FR-0.1) |
| Client declares a mode that doesn't match server `required_mode` | Rejected unconditionally before any cryptographic verification runs (SR-1) |
| Client substitutes a different KEM ciphertext or public key post-encapsulation | Detected — both are bound into the HKDF `info` parameter (SR-7) |
| A challenge/token/backup-code/push-approval is replayed | Rejected via `ReplayStore` consume-once; second attempt never succeeds, regardless of timing |
| A length-prefixed field in the wire format claims a length larger than the remaining buffer | Rejected as malformed input, caught by the same fuzz-tested parser path — never an out-of-bounds read |

## Session & rate limiting

| What happens if... | Required behavior |
|---|---|
| A subject exceeds their per-identity rate limit | `429`-equivalent rejection; independent of the global limiter's state |
| Global rate limit is exceeded even though no single identity is over their own limit | Still rejected — the two limiters are independent gates, not one merged counter |
| A session token is requested before all configured factors (primary + Layer 5 if configured) have passed | Never issued — token minting is the literal last statement after every gate passes, with no exception path that leaves a live token behind (SR-10) |
| Two verifiers in the same deployment are configured with different `required_mode` values for the same role | This is a config error, not a runtime ambiguity — `AlgorithmRegistry` roles are the single source of truth per role name; if two components disagree, that's an operator misconfiguration to catch at registry-load time, not something the runtime silently reconciles |

## Key custody (Layer 6–7)

| What happens if... | Required behavior |
|---|---|
| Vault file is corrupted | Explicit raised error — never a silently-returned empty result (SR-9) |
| Vault metadata is tampered with but payload ciphertext is untouched | Detected — metadata is inside the AEAD AAD, not stored unauthenticated alongside it |
| `HsmPkcs11Backend` or `OSKeychainBackend` is requested but not actually available/integrated in the current environment | Raises `NotImplementedError` / `BackendUnavailableError` explicitly — never silently behaves like an in-memory dict (SR-6) |
| A backup code is reused after consumption | Rejected — same consume-once contract as any other replay-sensitive credential |
| A subject loses access to their key custody entirely (device lost, no backup codes left) | Out of QuantX's scope — recovery-without-any-factor is an identity-proofing/support-process decision for the integrating application, not something QuantX can or should silently solve cryptographically |

## Storage backend failures

| What happens if... | Required behavior |
|---|---|
| `InMemoryKVStore` hits its `max_entries` cap | Enforced hard cap, explicit rejection of new entries — not unbounded growth (SR-3) |
| Networked backend connection is lost mid-session | A stated, explicit decision (fail-closed vs. degrade) is implemented and documented — not an unhandled exception surfacing as a generic 500 (SR-4) |
| `KeyValueStore` backend is unreachable at REST-sidecar layer | Surfaced as `503 backend_unavailable`, not masked as a `401` or `500` (see `08-api-specification.md`) |

## Governance (Layer 8)

| What happens if... | Required behavior |
|---|---|
| A `ThresholdPolicy` is created with the same key listed twice | Rejected at policy-creation time, before any finalize attempt (SR-12) |
| Quorum is met but with N-1 real approvers plus one duplicate-key attempt | Never counts as quorum — the duplicate-key rejection at creation time (above) is what prevents this from ever being reachable at finalize time |
| More approvals arrive than required after quorum is already met | Extra approvals are simply not needed; `finalize()` executes once quorum is first reached and does not wait for or require the rest |

## Membership / anonymity proofs (Layer 9)

| What happens if... | Required behavior |
|---|---|
| A Merkle proof's path doesn't actually reach the claimed root | Verifier returns `False` — it must actually walk and check the path, not return a fixed/placeholder result (SR-2) |
| Someone asks to use `AnonymousProofBackend` before a scoped external audit exists for the concrete implementation | Raises `NotImplementedError` — no interim implementation ships under a claim of anonymity, regardless of where the rest of the build stands |
| `MerkleMembershipProof` is presented in client-facing material without the non-anonymity caveat | Not permitted — the caveat is required, not optional, on every surface (FR-9.3) |

## Compliance / observability (Layer 10)

| What happens if... | Required behavior |
|---|---|
| `TlsInspector` cannot verify the peer's certificate | The authenticated probe fails/flags accordingly; if a separate permissive (`CERT_NONE`) probe is explicitly enabled, its findings are tagged `"trust": "unverified"` — never presented as equally certain to a verified finding (SR-13) |
| `StaticSourceScanner` produces a result | Always shipped with its permanent best-effort/false-positive disclaimer, attached to the output itself — not just a one-time README note that gets separated from the output in practice (SR-15) |
| `ComplianceReportGenerator` is asked to report against a standard not in the current `StandardsCatalog` | Fails explicitly / reports "no data for this standard" — never silently omits it from the report without saying so |

## Config & registry

| What happens if... | Required behavior |
|---|---|
| An unsigned `AlgorithmRegistry` config is loaded in a context that requires signing (Recipe B/C) | Rejected at load time — the deployment does not start in a half-configured state |
| A registry role references an algorithm adapter that isn't registered/available | Fails at load/startup time, not at first use — this is a fail-fast requirement, not a runtime surprise |
| A `GATE_REVIEW_REQUIRED` component is deployed to something described as "production" without a logged sign-off | This is a process violation to catch in review, not something the runtime can enforce by itself — flagged here so it's an explicit checklist item, not assumed to be self-enforcing |

## What's explicitly not this doc's job

Business-continuity/disaster-recovery procedures for a client's own infrastructure, and legal handling of a security incident — those belong to the client engagement's own operational runbook, not QuantX's own error handling.
