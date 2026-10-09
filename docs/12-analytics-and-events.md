# QuantX — Analytics / Metrics Plan

**Status:** Pre-implementation · **Note:** deliberately not a funnel/DAU/MAU plan — QuantX has no self-serve signup (D3, `11-multi-tenancy-model.md`). What's measured here is system health and security posture, per deployment.

## Why this looks different from a typical SaaS metrics plan

There's no acquisition funnel to instrument. Every metric below exists to answer one of two questions: *"is the auth engine behaving correctly and safely,"* or *"is this useful evidence for a client conversation / compliance report."*

## Auth engine health (Layer 4+, per deployment)

| Metric | Why it matters |
|---|---|
| Challenge issuance rate | Baseline traffic signal |
| Verify success vs. failure rate, split by failure reason (bad signature / mode mismatch / replay / rate-limited) | A spike in mode-mismatch failures could indicate an actual downgrade attempt in progress, not just noise |
| Session-token issuance rate | |
| Replay-rejection count (`ReplayStore` consume-once trips) | Direct signal of replay attempts against challenges, tokens, backup codes, or push approvals |
| Rate-limit trip count, per-identity vs. global | Distinguishes one noisy subject from a broader attack pattern |

## Second factor (Layer 5)

| Metric | Why it matters |
|---|---|
| MFA step-up completion rate | Are subjects actually completing the second factor, or abandoning |
| TOTP rate-limit trips (separate counter from Layer 4's — FR-5.2) | Brute-force signal specific to the TOTP surface |
| Push approval latency | Operational health of `PushAuthenticator` |

## Key custody & recovery (Layer 6–7)

| Metric | Why it matters |
|---|---|
| Backup-code consumption rate | Recovery-flow usage signal |
| Custody backend error rate (`BackendUnavailableError` occurrences) | Directly surfaces SR-6-class failures — this should page someone, not just log |

## Governance (Layer 8)

| Metric | Why it matters |
|---|---|
| Threshold approval throughput (time-to-quorum) | Operational usefulness of the governance flow for a given client |
| Duplicate-key rejection count at policy creation | Confirms SR-12 is actually being exercised, not just theoretically present |

## Compliance (Layer 10)

| Metric | Why it matters |
|---|---|
| Scan run count, findings by severity | Direct client-facing deliverable — this is often the artifact a client actually pays attention to first |
| `TlsInspector` findings split by trust tag (`verified` vs `unverified`) | Lets a client (or you) weight findings by evidentiary strength, not treat every finding as equally certain |
| `StaticSourceScanner` findings, always paired with its disclaimer | Prevents a scan report from being read as more authoritative than it is (SR-15 at the reporting layer, not just the README) |

## Business/practice-level (not code-instrumented — tracked manually)

| Metric | Why it matters |
|---|---|
| Which recipe (A/B/C) each client engagement actually lands on | Validates whether the composition model is delivering real variety or converging on one shape in practice |
| `GATE_REVIEW_REQUIRED` sign-off completion rate across components | A leading indicator for how much of the system can honestly be called production-ready at any point in time |

## Explicitly not tracked

- No PII, no subject-identifying analytics beyond what's operationally necessary for rate-limiting/replay detection (which is already covered under `07-database-design.md`, not duplicated as an "analytics" concern).
- No cross-client aggregation — consistent with the per-deployment isolation model in `11-multi-tenancy-model.md`. Metrics are per-deployment; there's no central dashboard rolling up data across clients unless a specific client engagement asks for their own internal one.
