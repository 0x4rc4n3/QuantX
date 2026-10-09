# `README.md`

**Location:** `quantx/ (repo root)` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The repo's front door — what QuantX is, the four-call quickstart (`default_setup() → start() → finish() → validate()`), and pointers to `docs/` for the full requirements/architecture doc set.

## Required contents / behavior
- States what QuantX is: a crypto-agile, hybrid (classical + post-quantum) authentication engine, shipped as independently-publishable Python packages plus an optional REST sidecar (`01-product-requirements.md`).
- Shows the Recipe-A quickstart: `default_setup() → start() → finish() → validate()` (`03-user-stories-and-flows.md`).
- States the mandatory PQC backend statement (D-006) plainly, up front — not buried (`10-security-requirements.md`).
- Points to `AI_BUILDER_HANDOFF.md` and `BUILD_INSTRUCTIONS.md` for the implementation handoff and exact `.md`-to-source conversion rules, to `docs/00-index.md` for the full requirements/architecture doc set, and to `docs/adr/` for the current (at doc-generation time, entirely unreviewed) state of every `GATE_REVIEW_REQUIRED` component.
- Does **not** describe this repository's current tree as "production-ready" anywhere — at doc-generation time, this is a specification scaffold, not a built, reviewed system (`BUILD_PROMPT.md` §5, §7).

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`01-product-requirements.md`, `03-user-stories-and-flows.md`, `10-security-requirements.md`
