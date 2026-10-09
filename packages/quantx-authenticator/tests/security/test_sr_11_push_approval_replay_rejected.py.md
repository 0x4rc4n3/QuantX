# `test_sr_11_push_approval_replay_rejected.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms a consumed push approval cannot be replayed — `ReplayStore` consume-once semantics.

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `tests/security/`
- **Depends on:** `push_authenticator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 5
- **Depends on:** `push_authenticator.py`
- **Implements:** The mandatory automated security test for SR-11 (push-approval half).
- **Outside:** Backup-code replay — that's `quantx-wallet`'s own SR-11 test.
- **Inside:** Consume-once semantics for push approvals specifically.
- **Security notes:** This file **is** the SR-11 enforcement check for push approvals.

## Required behavior
- Issue a push approval and consume it once — succeeds.
- Attempt to consume the same `approval_id` again — must fail, regardless of timing.

## Inputs / outputs
- **In:** a single approval, consumed twice.
- **Out:** second attempt must fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A push approval is replayed → rejected — same consume-once contract as any other replay-sensitive credential (`13-error-and-edge-cases.md`).

## Security notes
- **SR-11.** Push/backup-code approvals are consumed through `ReplayStore` — single use, no replay.

## Mandatory tests this must pass
- This file *is* the mandatory SR-11 test for push approvals.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Backup-code replay — `quantx-wallet`'s own test.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
