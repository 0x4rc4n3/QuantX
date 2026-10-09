# QuantX — Source of Truth

**Status:** Pre-implementation, fresh start. No prior codebase, no prior audit. This doc set — this index plus the numbered docs 01 to 16 beside it — is the complete, authoritative source of truth for QuantX from here forward. It supersedes and replaces any earlier drafts in full, including anything that referenced a "v1," an "audit," or a phased roadmap. Read this file first.

## Vision

Organizations with RSA/ECC-dependent auth systems need to move to post-quantum cryptography before "harvest now, decrypt later" attacks make today's captured traffic readable once a cryptographically relevant quantum computer exists. Most have no crypto-agility — algorithms are hardcoded, swapping them means rewriting call sites. QuantX is a crypto-agile, hybrid (classical + PQC) authentication engine built so that swapping an algorithm, a storage backend, or a key-custody method is a constructor argument, never a rewrite. Full product framing in `01-product-requirements.md`.

## Decisions register

| # | Decision |
|---|---|
| D1 | Assemble existing cryptographic primitives (`cryptography` (pyca), for both classical and PQC); never hand-roll crypto math |
| D2 | Hybrid mode (classical + PQC combined) is the default posture; PQC-only and classical-only are explicit opt-in configs, never client-declared |
| D3 | Business model is migration consulting + custom composed auth per client, not generic multi-tenant SaaS |
| D4 | Second factor: offline TOTP/HOTP module, paired with the PQC signature as primary factor |
| D5 | Language: Python for the SDK core |
| D6 | Dependency/build tooling: `uv` (or `poetry`) for env + dependency pinning |
| D7 | Repo hosting: single monorepo, independently-publishable packages, one per architectural layer group |
| D8 | Performance/latency targets — **open**; set from real benchmarking once Layers 0–4 exist, not guessed now |
| D9 | Legal entity, funding approach, solo-vs-team execution — **open** |
| D10 | Every Layer-1 algorithm adapter ships together in one pass — no minimum-then-expand sequencing (SLH-DSA excepted: upstream-blocked, see D13) |
| D11 | TOTP/HOTP secret persistence goes live only once `KeyWallet` (Layer 6) exists — no throwaway interim secret store |
| D12 | No phased or deferred roadmap. Every layer gets built, in dependency order, to the same bar of quality. Nothing is gated behind "wait for a client to ask" |
| D13 | PQC backend is `cryptography` (pyca) `>=48,<51` (ML-KEM, ML-DSA); `liboqs` is dropped. SLH-DSA is blocked until pyca ships it, with no substitute library (D-006, accepted; D-010 pin policy) |
| D14 | Delivery model: private factory, generated source slice per client (D-011, `16-delivery-and-factory.md`) |
| D15 | Configuration-driven composition: one `quantx.yaml`, fail closed (D-012, `15-config-and-composition.md`) |
| D16 | Containers: only the REST sidecar and dev/CI, never one per component (D-013) |
| D17 | An option is `available` only after conformance and recipe end-to-end tests pass (D-014) |

## Non-negotiable principles

Every component, every review, checked against these:

1. Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
2. One algorithm per adapter file, forever — no `if family == "pqc"` branches anywhere above Layer 1.
3. Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
4. Mode is a server-side construction fact, never trusted from wire data.
5. No component invents its own persistence — everything stateful goes through `KeyValueStore`.
6. No docstring claims a capability the code doesn't actually have — unimplemented means `NotImplementedError`, not a silent stub.
7. Nothing is called "production-ready," "audited," or "reviewed" anywhere — code, doc, or client material — until it actually has been, by someone other than whoever wrote it (`10-security-requirements.md`).

## Doc set

| # | File | What it covers | Build-order layer(s) |
|---|---|---|---|
| 01 | `01-product-requirements.md` | PRD — product, users, problem, value proposition | All |
| 02 | `02-build-order.md` | The single, non-phased, dependency-ordered build sequence | All, in order |
| 03 | `03-user-stories-and-flows.md` | User stories and flows per capability | All |
| 04 | `04-functional-requirements.md` | Precise behavior required of each component | All |
| 05 | `05-non-functional-requirements.md` | Security, performance, scalability, availability, maintainability | All |
| 06 | `06-system-architecture.md` | Full layer/component reference — the standalone architecture spec | All |
| 07 | `07-database-design.md` | Data model — `KeyValueStore`-shaped, not relational | All |
| 08 | `08-api-specification.md` | REST sidecar contract | Layer 4 consumer |
| 09 | `09-auth-and-authorization.md` | Auth model exposed to subjects + who's authorized to operate QuantX | All |
| 10 | `10-security-requirements.md` | Security requirements register + review gates | All |
| 11 | `11-multi-tenancy-model.md` | Why classic multi-tenancy doesn't apply; what isolation means here | — |
| 12 | `12-analytics-and-events.md` | What gets measured and why | All |
| 13 | `13-error-and-edge-cases.md` | Required behavior for every failure mode | All |
| 14 | `14-directory-structure.md` | Canonical repository tree and package boundaries | All |
| — | `QUANTX-V2-ARCHITECTURE.md` | Versioned interface, wire-format and KEM-binding contract | 0-4 |
| — | `DECISIONS.md` | Decision log (D-001 onward) | All |
| — | `INFERENCE_TRIAGE.md` | Sorted list of open inference markers in the spec files | All |
| 15 | `15-config-and-composition.md` | `quantx.yaml` schema, validation rules, recipes, CLI (D-012) | Service, factory |
| 16 | `16-delivery-and-factory.md` | Private factory, source-slice delivery, licence checklist (D-011) | Factory |
| — | `../FINAL_PLAN.md` | One-page final plan: decisions, order of work, gates | All |

## Deliberately not produced

QuantX is a developer-facing SDK + REST sidecar, not an end-user web app:

- **UI/UX Wireframes / Screens** — no end-user UI. `QuantX-Architecture-Builder.html` remains a useful internal wiring-visualization tool, unaffected by this doc set — it's a utility, not a planning document.
- **Design System** — no UI, no design system.
- **Billing / Subscription Specification** — the business model (D3) is per-client consulting engagements. Commercial terms belong in a client SOW, not an engineering doc.

## How to keep this from drifting

Edit the relevant doc in the same commit as the code change that caused it — never let a doc drift out of sync silently. If a change is big enough to affect vision, a decision, or a principle above, log it below.

## Change log

- 2026-10-04 (later): D-007 to D-009 accepted and D-015 to D-017 added: production keys live in an HSM or KMS (`aws_kms`, `gcp_kms` backends added), signed payload `QuantX-SIG-v1`, small defaults, the service terminates TLS, regional PQC-only warning. Triage reduced to one open row.
- 2026-10-04: D-011 to D-014 accepted (private factory and per-client source slices, config-driven composition, containers, option gate). Docs 15 and 16 and `FINAL_PLAN.md` added. Build order steps 11 and 12 added. `factory/` and `service/cli.py` added to the tree.
- 2026-10-03: D-006 accepted (pyca replaces liboqs); D-010 added (`cryptography>=48,<51`, Python 3.11+); D-007, D-008, D-009 proposed. `14-directory-structure.md` added to the doc set table. Smoke vectors in `QUANTX-V2-ARCHITECTURE.md` corrected (draft.2). `INFERENCE_TRIAGE.md` added. Earlier: security register renumbered from the C1/M1 scheme to `SR-1`..`SR-15`; `14-directory-structure.md` and `QUANTX-V2-ARCHITECTURE.md` added.
