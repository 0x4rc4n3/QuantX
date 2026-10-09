# `test_vault_corruption_raises_not_silent_empty.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms a corrupted vault file raises an explicit error from `EncryptedFileBackend`, never silently returning an empty result (FR-6.3).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/security/`
- **Depends on:** `encrypted_file_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** `encrypted_file_backend.py`
- **Implements:** The mandatory foundational test for FR-6.3.
- **Outside:** SR-9's metadata-specific tampering scenario — separate file.
- **Inside:** Whole-file corruption handling.
- **Security notes:** This file **is** the FR-6.3 enforcement check.

## Required behavior
- Corrupt a vault file's bytes wholesale (not just metadata) and call `retrieve()`.
- Confirm an explicit error is raised, never an empty/`None` result.

## Inputs / outputs
- **In:** a corrupted vault file.
- **Out:** must raise, never return empty.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Vault file is corrupted → explicit raised error — never a silently-returned empty result (FR-6.3, `13-error-and-edge-cases.md`).

## Security notes
- **FR-6.3.**

## Mandatory tests this must pass
- This file *is* the mandatory test for this rule.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Metadata-only tampering — that's SR-9's own test.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`
