# `check_single_canonicalization_path.py`

**Location:** `tools/lint/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A CI lint check confirming nothing outside `jcs_canonicalizer.py` serializes structured data for signing — the automated enforcement mechanism behind SR-8/FR-0.4's "exactly one canonicalization path" requirement.

## Required contents / behavior
- Scans `packages/`/`service/` for any serialization call pattern that produces bytes destined for a `Signer.sign()`/`Verifier.verify()` call, outside of `jcs_canonicalizer.py` itself.
- Fails the build if a second canonicalization path is found anywhere in the tree.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`10-security-requirements.md`, `04-functional-requirements.md`
