# `check_docstring_contract.py`

**Location:** `tools/lint/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A CI lint check confirming every module docstring in `packages/`/`service/` states, in order: Layer, Depends on, Implements, Outside, Inside, and (where applicable) Wire format and Security notes — the fixed docstring contract order this whole doc set's own per-file schema mirrors (FR-X.1).

## Required contents / behavior
- Parses every `.py` module's docstring in `packages/` and `service/`.
- Fails the build if a required field is missing or the fields appear out of the fixed order (FR-X.1).
- This check's own existence is why `AI_AGENT_GUIDELINES.md`'s per-file schema and this docstring contract are kept in the same fixed order — so this same check design applies to both the eventual code and this doc set, unmodified.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`04-functional-requirements.md`
