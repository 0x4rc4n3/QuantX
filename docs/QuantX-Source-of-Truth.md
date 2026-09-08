# QuantX — Single Source of Truth (SSOT)

**Owner:** Mudassir Javed (0x4rc4n3)
**Status:** Living document — pre-implementation
**Companion files:** `QuantX-v2-Architecture.md` (the exact interface/wire-format spec — this doc never repeats those signatures, it points to them), `QuantX-Architecture-Builder.html` (visual wiring tool)

## 0. How to use this document

This is the one place you (or anyone else who joins later) should be able to read start-to-finish and know: what QuantX is, what's already decided, what order things get built in, what "done" means at each step, and what rules every line of code follows. When a decision changes, edit this file in the same commit/PR as the code change that caused it — never let it drift out of sync silently.

Anything marked **Confirmed** below is something you've already stated in planning. Anything marked **Recommended default** is my proposal, not yet locked — change it freely, it's just here so you're not starting from a blank page.

---

## 1. Vision & Problem

Organizations with RSA/ECC-dependent auth systems need to move to post-quantum cryptography before "harvest now, decrypt later" attacks make today's captured traffic readable once a cryptographically relevant quantum computer exists. Most orgs have no crypto-agility — algorithms are hardcoded, swapping them means rewriting call sites. QuantX is a crypto-agile, hybrid (classical + PQC) authentication engine built so that swapping an algorithm, a storage backend, or a key-custody method is a constructor argument, never a rewrite.

## 2. Product Definition

**Confirmed — QuantX is:**
- A modular authentication SDK (Python packages) + an optional REST sidecar container, built around hybrid classical+PQC signatures/KEMs.
- Built entirely on top of established, unmodified cryptographic libraries (`cryptography`, `liboqs`) — QuantX never implements cryptographic primitives itself, only orchestration, composition, and policy around them.
- The technical proof-point behind a PQC-migration consulting offering: custom composed auth per client (PQC + secret sharing for high-stakes approvals, ZKP if requested), not a one-size-fits-all SaaS signup.

**Confirmed — QuantX is not (yet):**
- Not FIPS-validated, not independently audited, not to be marketed as production-hardened until Section 11 gates are cleared.
- Not a replacement for `liboqs`'s own security posture — OQS's own documentation states liboqs is a research/prototyping library not currently recommended for production use protecting sensitive data. QuantX's HYBRID-required-by-default design exists specifically to hedge this (never worse than classical-only security, even if a PQC algorithm has an undiscovered flaw).

## 3. Business Model & Positioning

**Confirmed:** PQC migration consulting company, using QuantX as the reusable core + credibility asset. Each client engagement composes existing primitives (never new crypto) into a solution shaped for that client — e.g., PQC signatures + Shamir-style secret sharing for board-level approval workflows, offline TOTP/HOTP as the standard second factor paired with the PQC signature as primary factor.

**Recommended default:** lead with the *architecture spec + a working Recipe A demo* as the portfolio artifact when approaching first clients, not a finished multi-tenant SaaS product — the market already has funded, credentialed competitors (PQShield, SandboxAQ, ISARA, QuSecure, CryptoNext and others); a working, honestly-scoped demo plus consulting flexibility is a more realistic wedge than competing on product completeness on day one.

## 4. Decisions Log

| # | Decision | Status |
|---|---|---|
| D1 | Assemble existing cryptographic primitives (`cryptography`, `liboqs`); never hand-roll crypto math | Confirmed |
| D2 | Hybrid mode (classical + PQC combined) is the default posture; PQC-only and classical-only are explicit opt-in configs, never client-declared | Confirmed |
| D3 | Business model is migration consulting + custom composed auth per client, not generic multi-tenant SaaS | Confirmed |
| D4 | Second factor: offline TOTP/HOTP module, paired with PQC signature as primary factor | Confirmed |
| D5 | Language: Python for the SDK core | Confirmed (from existing spec's adapter code) |
| D6 | Dependency/build tooling: `uv` for env management, lockfile, and dependency pinning | Confirmed |
| D7 | Repo hosting: single monorepo with independently-publishable packages, lockstep versioning (all packages share one version number) | Confirmed |
| D8 | No performance/latency targets set yet | **Open — see §14** |
| D9 | No decision yet on legal entity, funding, or solo-vs-team execution | **Open — see §14** |

## 5. Non-Negotiable Principles

Carried over from the architecture spec — every phase and every PR is checked against these:

1. Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
2. One algorithm per adapter file, forever — no `if family == "pqc"` branches anywhere above Layer 1.
3. Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
4. Mode is a server-side construction fact, never trusted from wire data.
5. No component invents its own persistence — everything stateful goes through `KeyValueStore`.
6. No docstring claims a capability the code doesn't actually have — unimplemented means `NotImplementedError`, not a silent stub.

## 6. Architecture at a Glance

Full interface signatures, wire formats, and security notes live in `QuantX-v2-Architecture.md`. Summary:

| Layer | Contents | Phase built (see §12) |
|---|---|---|
| 0 | Foundational interfaces: `Signer`, `KEMProvider`, `Canonicalizer`, `Clock`, `KeyValueStore`, `ReplayStore`, `RateLimiter`, `EventSink`; shared types (`Mode`, `KeyPair`, `HybridKeyPair`, `Challenge`, `SessionToken`); exception hierarchy (`QuantXError` tree) | 0–1 |
| 1 | Algorithm adapters (Ed25519, ECDSA-P256, ML-DSA-65/87, SLH-DSA, X25519, ML-KEM-768/1024) + reference `KeyValueStore` impls | 1 |
| 2 | `SignatureCombiner`, `KEMCombiner` | 1 |
| 3 | `AlgorithmRegistry` | 1 |
| 4 | `ChallengeIssuer`, `SessionOrchestrator` | 1 |
| 5 | `TotpProvider`, `PushAuthenticator` | 2 |
| 6 | `KeyWallet` + storage backends (file, OS keychain, HSM) | 3 |
| 7 | `BackupCodeManager`, `DeviceLinker` | 3 |
| 8 | `ThresholdPolicy`, `ThresholdManager` | 5 |
| 9 | `MerkleMembershipProof`, `AnonymousProofBackend` (unimplemented) | 6 |
| 10 | `CryptoBOMModel`, scanners, `ComplianceReportGenerator` | 7 |

## 7. Technology Stack

| Purpose | Choice | Caveat |
|---|---|---|
| Classical crypto | `cryptography` (pyca) | Mature, audited, safe for production |
| PQC crypto | `liboqs` (via Python bindings) | **Research/prototyping library per OQS's own docs — not currently recommended for production use with sensitive data.** Mitigated by mandatory hybrid mode (D2). Must be swappable later for a FIPS-validated backend behind the same `Signer`/`KEMProvider` interface — the architecture already supports this with zero caller changes. |
| Canonicalization | RFC 8785 (JCS), custom `JCSCanonicalizer` | Reference impl, no external dep needed |
| State store (dev) | `InMemoryKVStore` | Demo/test only |
| State store (prod) | Redis (`RedisKVStore`) | Recommended default — swap-in per Recipe B |
| Config format | YAML, `yaml.safe_load` only | Never `yaml.load` |
| Testing | `pytest` | Recommended default |
| Linting/formatting | `ruff check` + `ruff format` | Recommended default — `ruff format` replaces `black` (same style, faster, single tool) |
| Type checking | `mypy --strict` | Recommended default |
| CI | GitHub Actions | Recommended default |
| Audit event emission | `EventSink` protocol (Layer 0) — `NullEventSink` default, pluggable | Recommended default |

## 8. Repository Structure

**Recommended default** — monorepo, one directory per publishable package, matching the SDK split already defined in the architecture doc:

```
quantx/
├── packages/
│   ├── quantx-core/                 # Layer 0 (interfaces, shared types, exceptions)
│   ├── quantx-crypto-adapters/      # Layer 1
│   ├── quantx-combiners/            # Layer 2
│   ├── quantx-session/              # Layers 3-4
│   ├── quantx-authenticator/        # Layer 5
│   ├── quantx-wallet/               # Layers 6-7
│   ├── quantx-threshold/            # Layer 8
│   ├── quantx-zkp/                  # Layer 9
│   └── quantx-compliance/           # Layer 10
├── service/                          # REST sidecar (Docker container)
├── docs/
│   ├── QuantX-v2-Architecture.md
│   ├── QuantX-Source-of-Truth.md     # this file
│   └── adr/                          # Architecture Decision Records
├── integration-tests/                # cross-package integration tests
├── examples/                         # demo scripts (Recipe A walkthrough, etc.)
├── .github/workflows/
├── .editorconfig
├── .pre-commit-config.yaml
├── pyproject.toml                    # workspace root (uv workspace)
└── README.md
```

**Test layout:** unit tests live inside each package (`packages/quantx-core/tests/`, etc.) and run per-package. Cross-package integration tests (e.g. full Recipe A end-to-end flow) live in `integration-tests/` at the repo root.

## 9. Coding Guidelines

**9.1 Language & tooling.** Python 3.11+. Every package has its own `pyproject.toml`. Dependencies pinned exactly (no `>=` ranges) for anything crypto-related.

**9.2 Component rules (enforced, not optional).**
- One public class/function set per file — its "Outside." If you can't describe the file's job in one sentence without "and," split it.
- Constructors take interfaces (typed as `Protocol`), never concrete sibling classes. The only exception is `AlgorithmRegistry`, which is explicitly the single place allowed to import every Layer-1 adapter.
- No module-level mutable singletons, ever.
- Every adapter (Layer 1) target size: ~30–60 lines. If longer, something belongs in a different layer.
- All exceptions inherit from the shared `QuantXError` hierarchy defined in the architecture doc (§3.10). Operational failures (backend down, vault corrupt) raise typed exceptions; verification failures return `False`, never raise.

**9.3 Docstring contract.** Every component's module docstring states, in this order: Layer, Depends on, Implements, Outside, Inside, Wire format (if any), Security notes (what it guarantees / explicitly does not), Fixes (audit finding ID, if any). This mirrors the architecture doc's spec-block format exactly — a reviewer should never need to open two documents to understand one component.

**9.4 Style & static analysis.** `ruff format` for formatting, `ruff check` for linting, `mypy --strict` for typing. All three run in pre-commit hooks and CI; no PR merges with any of them failing. A single `.editorconfig` at the repo root enforces consistent whitespace/encoding across editors.

**9.5 Git/PR workflow (recommended default).**
- Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`).
- One component (or one tightly related group, e.g. an adapter + its test) per PR.
- Any PR touching a `GATE_REVIEW_REQUIRED` component requires the checklist in §11.1 completed in the PR description before merge.

**9.6 Versioning.** All packages use lockstep versioning — every package shares a single version number, bumped together. This simplifies cross-package dependency declarations (each package can declare `quantx-core == <same-version>`) and avoids the combinatorial compatibility matrix that independent versioning creates at this scale. Version is sourced from a single `VERSION` file at the repo root, read by each package's `pyproject.toml` via `dynamic = ["version"]`.

## 10. Testing Requirements

**10.1 Coverage.** Every Layer-0/1/2 component needs unit tests before it's considered done — no exceptions, these are the security-critical layers.

**10.2 Mandatory security tests.** Carried over as hard requirements from the architecture doc, not optional nice-to-haves:
- Every `SignatureCombiner` instance: the downgrade test (produce a real HYBRID signature, strip the PQC component, rewrite the declared-mode byte, assert `verify()` returns `False`).
- Every `ReplayStore`-gated flow: replay a consumed token, assert rejection.
- Every `RateLimiter`-gated flow: exceed the limit, assert rejection; test both per-identity and global limiter.
- `KEMCombiner`: mismatched-ciphertext substitution test (confirms M1's HKDF-binding fix actually rejects substitution).

**10.3 CI requirements.** Full test suite + lint + type-check on every PR. No merge to `main` on red CI, no exceptions.

## 11. Security & Review Gates

**11.1 `GATE_REVIEW_REQUIRED` components.** Per the architecture doc, in priority order: `SignatureCombiner`, `KEMCombiner`, `ThresholdManager`/`ThresholdPolicy`, `MerkleMembershipProof`, and whatever eventually implements `AnonymousProofBackend`. None of these get a "production-ready" label in any doc, README, or pitch material until an outside reviewer (not you alone) has signed off against the specific test obligations in the architecture doc. Track sign-off as a checklist item in the PR, and log it in `docs/adr/`.

**11.2 liboqs disclaimer requirement.** Any README, package description, or client-facing material that touches a `liboqs`-backed adapter must state plainly that the underlying PQC implementation is research-grade per its maintainers, and that hybrid mode is the mitigation. This is not optional — it's the honesty principle in §5.6 applied to your own marketing, not just your code.

**11.3 Dependency management.** Pin `liboqs` to a specific reviewed version; check its security advisories before every bump. Never build with experimental/non-standardized algorithms enabled by default.

## 12. Phased Roadmap

Each phase lists: Goal, What gets built, Depends on, Definition of Done, Explicit non-goals (what you're deliberately *not* doing yet).

### Phase 0 — Scaffolding
- **Goal:** a repo that can actually receive code.
- **Builds:** repo structure (§8), `uv` workspace root `pyproject.toml` + per-package `pyproject.toml`, CI skeleton (GitHub Actions: test + lint + typecheck), `.pre-commit-config.yaml` (`ruff check`, `ruff format`, `mypy --strict`), `.editorconfig`, empty `Protocol` stubs for all Layer-0 interfaces, shared types (§3.8 of the architecture doc), and the exception hierarchy (§3.10).
- **Depends on:** nothing.
- **Done when:** `pytest`/`ruff`/`mypy` all run green on an empty scaffold in CI, and `uv sync` installs the workspace with all packages resolvable.
- **Non-goals:** no real crypto code yet.

### Phase 1 — Core crypto-agile engine (Layers 0–4)
- **Goal:** a working end-to-end hybrid-auth demo — this is the actual product differentiator and your primary demo asset.
- **Builds:** all Layer 0 interfaces + `InMemoryKVStore`; Layer 1 adapters for at minimum Ed25519 + ML-DSA-65 (add ML-DSA-87/SLH-DSA/X25519/ML-KEM once the pattern is proven); `SignatureCombiner`, `KEMCombiner`; `AlgorithmRegistry`; `ChallengeIssuer`, `SessionOrchestrator`. This is exactly Recipe A from the architecture doc. A `NullEventSink` (silent default) ships alongside all Layer-4 components; real event sinks are plugged in at deployment time.
- **Depends on:** Phase 0.
- **Done when:** the three-call demo (`default_setup()` → `start()` → `finish()` → `validate()`) works end-to-end, plus all §10.2 security tests pass, plus §11.1 sign-off obtained for `SignatureCombiner`/`KEMCombiner`.
- **Non-goals:** no MFA, no persistence beyond in-memory, no key custody beyond raw keys in memory.

### Phase 2 — Second factor (Layer 5, partial)
- **Goal:** MFA flow demo.
- **Builds:** `TotpProvider` (offline TOTP/HOTP per D4).
- **Depends on:** Phase 1.
- **Done when:** TOTP verification integrates into `SessionOrchestrator` as an additional gate, with its own rate-limit test.
- **Non-goals:** `PushAuthenticator` deferred — online push MFA isn't needed until a client asks for it.

### Phase 3 — Key custody & recovery (Layers 6–7, partial)
- **Goal:** keys survive process restarts safely.
- **Builds:** `KeyWallet` + `EncryptedFileBackend`; `BackupCodeManager`.
- **Depends on:** Phase 1.
- **Done when:** vault metadata is AAD-authenticated (per M3 fix), corruption raises rather than silently returning empty, backup codes single-use-verified. Key rotation semantics are defined and tested: `rotate()` generates a new keypair, archives the old key material with a `retired_at` timestamp (retrievable via `list_keys()` with `include_retired=True`), and a configurable grace period allows signature verification with the retired key for a bounded window after rotation.
- **Non-goals:** `OSKeychainBackend` and `HsmPkcs11Backend` deferred until a specific client's environment requires them — build the real integration when it's needed, not speculatively.

### Phase 4 — Production hardening (Recipe B)
- **Goal:** the system can run horizontally scaled, not just single-process.
- **Builds:** `RedisKVStore`; signed `algorithm_registry.yaml` loading path.
- **Depends on:** Phases 1–3.
- **Done when:** swapping `InMemoryKVStore` → `RedisKVStore` requires zero changes to any Phase 1–3 component (this is the actual test of whether the architecture's core promise holds).
- **Non-goals:** no auto-scaling infra, no multi-region — just prove horizontal scaling works.

### Phase 5 — Governance (Layer 8) — build on client demand
- **Goal:** threshold/quorum approval for high-value actions (e.g., board-level sign-off use case from D3).
- **Builds:** `ThresholdPolicy`, `ThresholdManager`.
- **Depends on:** Phase 1.
- **Done when:** duplicate-key rejection test passes, §11.1 sign-off obtained.
- **Non-goals:** don't build this speculatively — wait for an actual client use case, per D3's "custom composed per client" model.

### Phase 6 — Privacy/membership proofs (Layer 9) — build on client demand
- **Goal:** sound (non-anonymous) membership proofs where a client asks for ZKP-adjacent capability.
- **Builds:** `MerkleMembershipProof` only. `AnonymousProofBackend` stays `NotImplementedError` until a funded, scoped audit is possible for whatever specific implementation goes behind it.
- **Depends on:** Phase 1.
- **Done when:** §11.1 sign-off obtained; any UI or doc surfacing this feature makes the non-anonymity caveat impossible to miss.

### Phase 7 — Observability & compliance (Layer 10) — parallel-track, useful for consulting
- **Goal:** a crypto-inventory/compliance-report tool — genuinely useful as its own consulting lead-gen asset, independent of the auth engine.
- **Builds:** `CryptoBOMModel`, `StaticSourceScanner`, `TlsInspector`, `StandardsCatalog`, `ComplianceReportGenerator`.
- **Depends on:** nothing else — can be built in parallel with Phases 2–6 if useful for client conversations sooner.
- **Done when:** scanner README states false-positive/negative caveat; `TlsInspector` output correctly tags trust level per probe type.

### Phase 8 — Packaging & first external use
- **Goal:** something a client or collaborator can actually install.
- **Builds:** PyPI packages for whichever SDK packages are ready; the Docker container fronting `SessionOrchestrator` via REST (`/challenge`, `/verify`, `/session/:id`).
- **Depends on:** Phase 1 minimum; more phases = more capability to offer.
- **Non-goals:** don't wait for every phase — package and show Phase 1 alone if that's what gets the first client conversation moving.

## 13. Global Definition of Done

Applies to every component, every phase:
- [ ] Unit tests pass, including any mandatory security test from §10.2 that applies
- [ ] Docstring follows the §9.3 contract completely
- [ ] No import of a sibling concrete class above Layer 1 (except `AlgorithmRegistry`)
- [ ] All exceptions inherit from the `QuantXError` hierarchy (§3.10 of the architecture doc); no bare `Exception` or `ValueError` raises for domain-specific failures
- [ ] `ruff check`, `ruff format`, `mypy --strict` all pass
- [ ] If `GATE_REVIEW_REQUIRED`: §11.1 checklist completed and logged in `docs/adr/`
- [ ] If it touches `liboqs`: §11.2 disclaimer present in its README

## 14. Open Questions — needs your decision, not invented here

- Performance/latency targets (D8) — set these during Phase 1 benchmarking against real hardware, not before.
- Legal entity, funding approach, solo vs. team execution (D9).
- Which specific PQC algorithm set ships as the *default* role in `algorithm_registry.yaml` beyond the Phase 1 minimum (Ed25519 + ML-DSA-65) — likely settles itself once Phase 1's demo is working and you see what a first client actually asks for.

## 15. Change Log

Record every material change here with a date and one line — this is what keeps the document trustworthy as "current" rather than "aspirational."

- **2026-09-08** — Foundational fixes before Phase 0 coding: confirmed D6 (`uv`) and D7 (monorepo + lockstep versioning); replaced `black` with `ruff format` everywhere; added `quantx-core` package for Layer-0 types/exceptions; defined `§9.6 Versioning`; added `EventSink` to tech stack; expanded Phase 0/1/3 builds and done-when criteria; corrected repo structure (per-package tests, integration-tests/, .editorconfig, .pre-commit-config.yaml); added `QuantXError` hierarchy to Global DoD; updated §6 architecture summary for new Layer-0 content; removed resolved open questions (D6, D7).

## 16. References

- `QuantX-v2-Architecture.md` — full component specs, wire formats, audit-finding traceability
- `QuantX-Architecture-Builder.html` — visual component-wiring tool
