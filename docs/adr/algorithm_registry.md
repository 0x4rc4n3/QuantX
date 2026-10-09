# `algorithm_registry.md`

**Location:** `docs/adr/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The architecture decision record where `AlgorithmRegistry`'s eventual outside-reviewer sign-off gets logged, per `BUILD_PROMPT.md` §5's `GATE_REVIEW_REQUIRED` notice.

## Required contents / behavior
- **Components covered:** `packages/quantx-registry/src/quantx_registry/algorithm_registry.py`
- **Status at doc-generation time: UNREVIEWED.** No sign-off has been logged — none of the components above may be called "production-ready" in any doc, README, or client material until someone *other than the implementing author* has reviewed the eventual implementation and logged that review here.
- **What the reviewer should confirm:** That this remains the sole file importing every Layer-1 adapter directly, and that unsigned config is rejected outside explicit dev/demo `allow_unsigned=True` use (FR-3.1, FR-3.3).
- **Sign-off log:** *(empty — to be filled in in a future pass, once implementation and outside review actually happen. An AI coding agent completing the components above is the author for gate-review purposes, and may not sign off on its own work here.)*

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
