# `test_sr_11_backup_code_replay_rejected.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms a consumed backup code cannot be reused — the backup-code half of SR-11 (the push-approval half lives in `quantx-authenticator`).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/security/`
- **Depends on:** `backup_code_manager.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6-7
- **Depends on:** `backup_code_manager.py`
- **Implements:** The mandatory automated security test for SR-11 (backup-code half).
- **Outside:** The push-approval half — `quantx-authenticator`'s own test.
- **Inside:** Consume-once semantics for backup codes specifically.
- **Security notes:** This file **is** the SR-11 enforcement check for backup codes.

## Required behavior
- Verify a genuine backup code once — succeeds.
- Attempt to verify the same code again — must fail, regardless of timing.

## Inputs / outputs
- **In:** a single code, verified twice.
- **Out:** second attempt must fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A backup code is reused after consumption → rejected — same consume-once contract as any other replay-sensitive credential (`13-error-and-edge-cases.md`).

## Security notes
- **SR-11.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-11 test for backup codes.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Push-approval replay — `quantx-authenticator`'s own test.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
