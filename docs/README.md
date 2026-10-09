# `docs/` — foundational source-of-truth docs, and this scaffold's own root

## What this is
The 15 foundational documents (`00-index.md` through `14-directory-structure.md`) this scaffold was generated from, plus the versioned replacement architecture contract, the decision log, and `adr/`, where every `GATE_REVIEW_REQUIRED` component's eventual review sign-off gets logged. The foundational documents are source material; the replacement contract and decision log are maintained documents.

## Part of
Top-level.

## Contains
- `00-index.md` … `14-directory-structure.md` — the 15 foundational source docs
- `QUANTX-V2-ARCHITECTURE.md` — versioned normative interface, wire-format, session, and sidecar contract for implementation
- `DECISIONS.md` — accepted decisions, unresolved choices, and change protocol
- `15-config-and-composition.md` and `16-delivery-and-factory.md` — configuration-driven composition and the private delivery model
- `INFERENCE_TRIAGE.md` — open inference markers sorted into resolved, must-decide and acceptable
- `adr/` — one file per `GATE_REVIEW_REQUIRED` component group, where review sign-off gets logged

## Why divided this way
The foundational docs remain under `docs/`, and the versioned architecture contract is maintained beside them so every generated spec file in `packages/`/`service/` can cite a precise contract without ambiguity about which version was used.

## Dependency rules
- Every generated `.py.md` spec file in this scaffold cites one or more of these 15 docs under `Source docs` — nothing in `packages/`/`service/` should ever contradict them without that contradiction being flagged for human review (`AI_AGENT_GUIDELINES.md` §1c).

## Source docs
`00-index.md`
