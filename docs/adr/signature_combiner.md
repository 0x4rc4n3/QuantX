# `signature_combiner.md`

**Location:** `docs/adr/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The architecture decision record where `SignatureCombiner` and `signature_mode_enforcement.py`'s eventual outside-reviewer sign-off gets logged, per `BUILD_PROMPT.md` §5's `GATE_REVIEW_REQUIRED` notice.

## Required contents / behavior
- **Components covered:** `packages/quantx-combiners/src/quantx_combiners/signature/signature_combiner.py`, `.../signature_mode_enforcement.py`
- **Status at doc-generation time: UNREVIEWED.** No sign-off has been logged — none of the components above may be called "production-ready" in any doc, README, or client material until someone *other than the implementing author* has reviewed the eventual implementation and logged that review here.
- **What the reviewer should confirm:** That `required_mode` is fixed at construction and never influenced by wire data, and that verification never proceeds before the mode check has passed (SR-1).
- **Sign-off log:** *(empty — to be filled in in a future pass, once implementation and outside review actually happen. An AI coding agent completing the components above is the author for gate-review purposes, and may not sign off on its own work here.)*

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
