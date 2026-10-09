# `check_no_sibling_imports.py`

**Location:** `tools/lint/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A CI lint check confirming no component above Layer 1 imports a sibling concrete class instead of a Layer-0 interface — except `AlgorithmRegistry`, the one named, deliberate exception (FR-X.2, FR-3.1).

## Required contents / behavior
- Scans import statements across `packages/`/`service/`.
- Fails the build on any Layer-2-or-above file importing a concrete class from a sibling module at the same or a lower non-Layer-0 layer, with `algorithm_registry.py`'s imports of every Layer-1 adapter as the sole allowed exception.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`04-functional-requirements.md`
