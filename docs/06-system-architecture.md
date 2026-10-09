# QuantX — System Architecture

**Status:** Pre-implementation · This is the standalone architecture reference — layers, components, repo shape, tech stack, and component-level rules. Exact interface signatures and wire formats get written directly into each component's module docstring as it's built (per the contract in "Component & repo rules" below), so they live with the code rather than in a second document that can drift out of sync.

## Shape of the system

QuantX is a layered library, not a service, with a thin optional service wrapper (the REST sidecar) on top. Dependencies point one direction only: a layer may depend on layers below it, never above, and never sideways — with one named exception: `AlgorithmRegistry` (Layer 3) is the single place allowed to import every Layer-1 adapter directly.

## Layers and components

| Layer | Contents |
|---|---|
| 0 | Foundational interfaces: `Signer`, `Verifier`, `KEMProvider`, `Canonicalizer`, `Clock`, `KeyValueStore`, `ReplayStore`, `RateLimiter` — plus reference implementations `InMemoryKVStore`, `JCSCanonicalizer` |
| 1 | Algorithm adapters: Ed25519, ECDSA-P256, ML-DSA-65, ML-DSA-87, X25519, ML-KEM-768, ML-KEM-1024 (SLH-DSA specified, upstream-blocked, D-006) |
| 2 | `SignatureCombiner`, `KEMCombiner` |
| 3 | `AlgorithmRegistry` |
| 4 | `ChallengeIssuer`, `SessionOrchestrator` |
| 5 | `TotpProvider`, `PushAuthenticator` |
| 6–7 | `KeyWallet` + backends (`EncryptedFileBackend`, `OSKeychainBackend`, `HsmPkcs11Backend`); `BackupCodeManager`, `DeviceLinker` |
| 8 | `ThresholdPolicy`, `ThresholdManager` |
| 9 | `MerkleMembershipProof`; `AnonymousProofBackend` (interface only, unimplemented) |
| 10 | `CryptoBOMModel`, `StaticSourceScanner`, `TlsInspector`, `StandardsCatalog`, `ComplianceReportGenerator` |

Build order across these layers is `02-build-order.md`, not this doc — this table is the "what," not the "when."

## Composition, not configuration flags

There's no single "QuantX class" with a mode enum. Different deployments are literally different object graphs wired from the same components — this is what "crypto-agile" means concretely. These are **deployment compositions**, available as soon as their underlying layers are built — not phase-gated, and a given client's deployment can legitimately compose only up through whichever layer it needs, even though QuantX itself builds every layer:

- **Recipe A — Demo/dev.** In-memory everything, unsigned registry config, raw keys in memory.
- **Recipe B — Enterprise.** Networked `KeyValueStore` backend, signed `AlgorithmRegistry` config, `KeyWallet` on a real backend (HSM/keychain).
- **Recipe C — PQC-only regulated environment.** Same components, `required_mode` set to PQC-only at the registry level. No new code — a different registry role plus a different constructor argument. (Note: this removes hybrid mode's hedge against an undiscovered PQC flaw — see `10-security-requirements.md`'s PQC backend statement before deploying this recipe for a client.)

## Repository structure

Monorepo, one directory per publishable package, matching the layer boundaries so a client can depend on just the algorithm-agility layer without pulling in governance or compliance tooling. The tree below is canonical and agrees with `14-directory-structure.md`:

```
quantx/
├── packages/
│   ├── quantx-core/              # Layer 0
│   ├── quantx-crypto-adapters/   # Layer 1
│   ├── quantx-combiners/         # Layer 2
│   ├── quantx-registry/          # Layer 3
│   ├── quantx-session/            # Layer 4
│   ├── quantx-authenticator/      # Layer 5
│   ├── quantx-wallet/             # Layers 6-7
│   ├── quantx-threshold/          # Layer 8
│   ├── quantx-zkp/                # Layer 9
│   └── quantx-compliance/         # Layer 10
├── service/                      # REST sidecar (Docker container)
├── docs/                         # requirements, architecture, decisions, and builder guidance
│   └── adr/                      # Architecture Decision Records + GATE_REVIEW sign-offs, one file per
├── tests/
└── .github/workflows/
```

## Tech stack

| Purpose | Choice | Note |
|---|---|---|
| Classical crypto | `cryptography` (pyca) | Mature, audited, safe for production |
| PQC crypto | `cryptography` (pyca) `>=48,<51` | ML-KEM and ML-DSA (FIPS 203/204) via the wheel's OpenSSL >=3.5 backend, or AWS-LC/BoringSSL builds. Newer modules than the classical ones; mitigated by mandatory hybrid mode (D2). No SLH-DSA upstream yet (D-006). Any FIPS validation status depends on the backend build, not on QuantX; swapping backends needs no caller changes |
| Canonicalization | RFC 8785 (JCS), custom `JCSCanonicalizer` | Reference impl, no external dependency needed |
| State store (dev) | `InMemoryKVStore` | Demo/test only, hard `max_entries` cap |
| State store (production) | Networked backend (e.g. Redis) | Swap-in per Recipe B, zero changes to Layers 1–4 |
| Config format | YAML, `yaml.safe_load` only | Never `yaml.load` |
| Sidecar transport | HTTPS, hybrid TLS 1.3 group (e.g. X25519MLKEM768) | Never plaintext HTTP, even in dev; the sidecar's own transport shouldn't be the classical-only weak link in a PQC-migration product |
| Testing | `pytest` + Hypothesis (property-based) | |
| Linting/formatting | `ruff` + `black` | |
| Type checking | `mypy --strict` | |
| CI | GitHub Actions | |

QuantX itself never implements a primitive — it wraps and combines (D1).

## Component & repo rules

- Python 3.11+. Every package has its own `pyproject.toml`. Crypto-related dependencies are pinned exactly in the lockfile (D6) that CI and service images install from; package metadata may declare only a bounded, reviewed range (D-010), e.g. `cryptography>=48,<51`. Open-ended `>=` ranges are not allowed.
- One public class/function set per file. If the file's job can't be described in one sentence without "and," split it.
- Constructors take interfaces (`Protocol`-typed), never concrete sibling classes — the only exception is `AlgorithmRegistry`.
- No module-level mutable singletons, ever.
- Every Layer-1 adapter target size: ~30–60 lines.
- Docstring contract, every component, in this order: **Layer, Depends on, Implements, Outside, Inside, Wire format (if any), Security notes (what it guarantees / explicitly does not).** A reviewer should never need to open a second document to understand one component.
- Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`). One component (or tightly related group, e.g. an adapter + its test) per PR. Any PR touching a `GATE_REVIEW_REQUIRED` component requires the checklist in `10-security-requirements.md` completed in the PR description before merge.

## What's deliberately not decided here

Concrete performance targets (D8) — the architecture is designed to be measured once Layers 0–4 exist, not pre-tuned to a guessed number.
