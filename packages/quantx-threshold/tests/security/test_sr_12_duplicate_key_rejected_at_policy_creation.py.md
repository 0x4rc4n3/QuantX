# `test_sr_12_duplicate_key_rejected_at_policy_creation.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `ThresholdPolicy` rejects a key set containing a duplicate at construction time, before any approval is ever submitted.

## Part of / dependency graph
- **Package:** `quantx-threshold`, `tests/security/`
- **Depends on:** `threshold_policy.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 8
- **Depends on:** `threshold_policy.py`
- **Implements:** The mandatory automated security test for SR-12.
- **Outside:** Runtime approval tracking — `threshold_manager.py`'s own test.
- **Inside:** Duplicate-key rejection at construction.
- **Security notes:** This file **is** the SR-12 enforcement check.

## Required behavior
- Construct a `ThresholdPolicy` with the same key appearing twice in the key set.
- Confirm construction is rejected — never succeeds with a degenerate policy where one key could count twice toward quorum.

## Inputs / outputs
- **In:** a key set with a duplicate.
- **Out:** must reject at construction.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A threshold policy is constructed with a duplicate key → rejected at creation, not at use (`13-error-and-edge-cases.md`).

## Security notes
- **SR-12.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-12 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Runtime approval tracking — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
