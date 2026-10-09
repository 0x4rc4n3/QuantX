# `test_replay_and_rate_limit_rejection.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The foundational (no single SR number) test confirming `SessionOrchestrator` correctly rejects replayed challenges/tokens and independently enforces per-identity and global rate limits (FR-4.2, FR-4.4).

## Part of / dependency graph
- **Package:** `quantx-session`, `tests/security/`
- **Depends on:** `session_orchestrator.py`; `ReplayStore`, `RateLimiter` (Layer 0)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 4
- **Depends on:** `session_orchestrator.py`, Layer-0 `ReplayStore`/`RateLimiter`
- **Implements:** Mandatory security tests 2 and 3 from `10-security-requirements.md`, at the session-orchestrator level.
- **Outside:** SR-10 mint-ordering — separate file.
- **Inside:** Replay-after-consume and both limiters tripping independently.
- **Security notes:** This file covers mandatory tests 2 (replay rejection) and 3 (rate-limit rejection).

## Required behavior
- Consuming a challenge/token once succeeds; a second attempt with the same value is rejected via `ReplayStore` consume-once semantics, regardless of timing.
- Exceeding the per-identity limit rejects, independent of the global limiter's state.
- Exceeding the global limit rejects even when no single identity is individually over their own limit — the two limiters are independent gates, not a merged counter.

## Inputs / outputs
- **In:** replay attempts, rate-limit-tripping request volumes.
- **Out:** must reject in both scenarios.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A challenge/token is replayed → rejected via `ReplayStore` consume-once; second attempt never succeeds, regardless of timing (`13-error-and-edge-cases.md`).

## Security notes
- **Mandatory tests 2 and 3 (`10-security-requirements.md`).**

## Mandatory tests this must pass
- This file *is* the mandatory replay/rate-limit test at the session-orchestrator level.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- SR-10 mint-ordering — separate file.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
