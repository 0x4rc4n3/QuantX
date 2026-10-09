# QuantX — Product Requirements Document (PRD)

**Status:** Pre-implementation · **Depends on:** `00-index.md` (vision, decisions register, principles) — this doc expands that into PRD shape

## Product

QuantX is a crypto-agile, hybrid (classical + post-quantum) authentication engine, shipped as a set of independently-publishable Python packages plus an optional REST sidecar container. It is the technical proof-point behind a post-quantum-migration consulting practice.

## Problem

Organizations whose authentication systems depend on RSA/ECC face two compounding problems:

1. **"Harvest now, decrypt later."** Traffic captured today can be decrypted retroactively once a cryptographically relevant quantum computer exists. Migration needs to start before that computer exists, not after.
2. **No crypto-agility.** In most existing systems, the choice of signature/KEM algorithm is hardcoded through the call stack. Swapping an algorithm — or even running two algorithms side-by-side during a migration window — means touching every call site, not changing a config value.

QuantX exists to make (2) untrue, so that (1) can actually be acted on without a rewrite.

## Target users

QuantX has no self-serve end user. Its users are:

- **Integrating developers** — engineers at a client organization (or the consulting practice itself) who wire QuantX's packages into an existing system.
- **Subjects** — the humans or services who ultimately authenticate through a system that has QuantX behind it. They never interact with QuantX directly.
- **Relying-party operators** — whoever runs the verifying side of a deployment (session issuance, MFA policy, key custody choices).
- **Security/compliance auditors** — internal or third-party reviewers who need to sign off on `GATE_REVIEW_REQUIRED` components or consume the compliance-report tooling (Layer 10).
- **The consulting operator (you)** — composes the above roles differently per client engagement (D3).

## Core value proposition

Swapping an algorithm, a storage backend, or a key-custody method is a constructor argument, never a rewrite. This is proven, not asserted: swapping `InMemoryKVStore` for a networked backend (Recipe A → Recipe B, `06-system-architecture.md`) requires zero changes to any Layer 0–3 component.

## Core features (by layer — full specs in `06-system-architecture.md`)

1. Algorithm adapters for classical and PQC signature/KEM primitives, one file per algorithm (Layer 1) — all shipped together (D10).
2. Generic signature and KEM combiners that produce hybrid, PQC-only, or classical-only results depending on server-set mode — never client-declared (Layer 2).
3. An algorithm registry that maps named "roles" (e.g. `session-auth`) to a concrete pairing, loaded from YAML, signature-verified (Layer 3).
4. Challenge/response session issuance with replay and rate-limit protection (Layer 4).
5. Offline TOTP/HOTP second factor (Layer 5).
6. Key custody with swappable backends: encrypted file, OS keychain, HSM (Layer 6–7).
7. Threshold/quorum approval for high-value actions (Layer 8).
8. Sound (non-anonymous) membership proofs, with true anonymity isolated behind a mandatory-audit-gated, unimplemented-by-default interface (Layer 9).
9. A crypto-inventory/compliance-report tool usable independently of the auth engine (Layer 10).
10. PyPI packaging and a REST sidecar so a client can actually install and run it, surfaced as soon as Layer 4 is done.

## User journeys

See `03-user-stories-and-flows.md` for the full set. At PRD level, the journeys that matter:

1. An integrating developer wires Recipe A and gets a working hybrid-auth demo in three calls: `default_setup()` → `start()` → `finish()` → `validate()`.
2. A relying-party operator adds TOTP as a second gate without touching `SessionOrchestrator`'s internals.
3. An operator moves from a single process to horizontally-scaled by swapping one constructor argument (`InMemoryKVStore` → `RedisKVStore`).
4. A client with a board-approval use case gets threshold/quorum auth composed on top of the same primitives, not a new product.
5. An auditor works through the `GATE_REVIEW_REQUIRED` checklist (`10-security-requirements.md`) for a specific component before it's called production-ready anywhere.

## Business rules

- Hybrid mode is the default posture. PQC-only and classical-only are explicit opt-in server configs — a client can never request a mode by sending one on the wire (D2).
- QuantX never implements cryptographic primitives itself — only orchestration, composition, and policy around `cryptography` (D1).
- No component is labeled "production-ready" in any doc, README, or pitch material until its `GATE_REVIEW_REQUIRED` checklist is signed off by someone other than the author.
- Any material touching a PQC adapter carries the PQC backend statement: which library backs it, that its PQC support is recent, and no FIPS-validation claim unless the backend build is itself validated (D-006).
- Business model is per-client consulting composition, not generic multi-tenant SaaS (D3) — see `11-multi-tenancy-model.md` for what that means architecturally.

## Build target

See `02-build-order.md` for the full, non-phased build sequence. Every layer gets built, in dependency order, to the same bar of quality — there is no separate "MVP-only" cut of the product.

## Success metrics

Deliberately not funnel/DAU metrics — this isn't a self-serve product. See `12-analytics-and-events.md` for the full plan. At PRD level:

- The end-to-end demo (`default_setup()` → `start()` → `finish()` → `validate()`) runs with all mandatory security tests (`10-security-requirements.md`) passing.
- `SignatureCombiner`/`KEMCombiner` clear `GATE_REVIEW_REQUIRED` sign-off.
- Recipe A → Recipe B swap requires zero changes outside the wiring layer (the architecture's core claim, made falsifiable).
- At least one real client engagement uses QuantX as the technical basis for a composed solution (validates D3's business model, not just the code).

## Explicitly out of scope for QuantX as a product

- Self-serve signup, billing, or multi-tenant SaaS UI (D3; see `11-multi-tenancy-model.md`).
- FIPS validation or independent audit claims before every `GATE_REVIEW_REQUIRED` gate is actually cleared.
- Competing on product completeness against funded competitors (PQShield, SandboxAQ, ISARA, QuSecure, CryptoNext) — the wedge is the working demo plus consulting flexibility.
