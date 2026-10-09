# GENERATION_REPORT.md

This report is required by `AI_AGENT_GUIDELINES.md` §5. It covers the generation of this entire `quantx/` scaffold — the full source/test directory tree and its parallel `.md` spec tree — from the 15 foundational docs (`docs/00-index.md` through `docs/14-directory-structure.md`) plus `BUILD_PROMPT.md` and `AI_AGENT_GUIDELINES.md`.

## 0. Revision note (2026-10-03)

This report describes the original generation pass. After it, the scaffold was revised: `docs/INFERENCE_TRIAGE.md` and decisions D-007 to D-010 were added, D-006 was accepted, and the V2 architecture smoke vectors were corrected. The file counts in §1 describe the original pass and now differ by one new doc (`docs/INFERENCE_TRIAGE.md`). The inference inventory in §5 is historical; use `docs/INFERENCE_TRIAGE.md` for current status.

## 1. File counts vs. manifest

- **Manifest total (`BUILD_PROMPT.md` §6):** 277 paths, including this report itself and the 15 source docs already present under `docs/`.
- **Generated spec files (`.md` files this pass produced, excluding the 15 source docs and this report):** 276 — an exact match against the manifest, with **zero missing and zero extra** (path audit, `AI_AGENT_GUIDELINES.md` §4.1).
  - `full` schema (§3): 170
  - `value` schema (§3a, lighter): 11
  - `README.md` (§4): 66
  - `other` (non-`.py` root/config/CI/ADR files not literally covered by §3/§3a/§4 — see §6 of this report): 29
- **Source-of-truth docs copied into `docs/` unmodified:** 15.
- **`GATE_REVIEW_REQUIRED` files:** 12, matching `BUILD_PROMPT.md` §5's list exactly (gate-review granularity check, `AI_AGENT_GUIDELINES.md` §4.5):
  - `packages/quantx-combiners/src/quantx_combiners/kem/kem_combiner.py.md`
  - `packages/quantx-combiners/src/quantx_combiners/kem/kem_hkdf_binding.py.md`
  - `packages/quantx-combiners/src/quantx_combiners/signature/signature_combiner.py.md`
  - `packages/quantx-combiners/src/quantx_combiners/signature/signature_mode_enforcement.py.md`
  - `packages/quantx-registry/src/quantx_registry/algorithm_registry.py.md`
  - `packages/quantx-threshold/src/quantx_threshold/threshold_manager.py.md`
  - `packages/quantx-threshold/src/quantx_threshold/threshold_policy.py.md`
  - `packages/quantx-wallet/src/quantx_wallet/backends/encrypted_file_backend.py.md`
  - `packages/quantx-wallet/src/quantx_wallet/backends/hsm_pkcs11_backend.py.md`
  - `packages/quantx-wallet/src/quantx_wallet/backends/os_keychain_backend.py.md`
  - `packages/quantx-zkp/src/quantx_zkp/anonymous_proof_backend.py.md`
  - `packages/quantx-zkp/src/quantx_zkp/merkle_membership_proof.py.md`

## 2. Deviations from a literal reading of the manifest, and why

None in the final pass. One was caught and corrected during generation, by the path-audit self-check (`AI_AGENT_GUIDELINES.md` §4.1): an extra, unlisted `packages/quantx-combiners/src/quantx_combiners/README.md` was drafted (a source-root README one level above `signature/` and `kem/`), found not to appear in `BUILD_PROMPT.md` §6's tree, and removed before this pass.

## 3. Known doc-set contradictions and bookkeeping gaps

- **`14-directory-structure.md` vs. `06-system-architecture.md` on repo layout.** The uploaded `06-system-architecture.md` contained an older 8-package grouping. The builder-readiness revision corrected it to the 10-package layout in `14-directory-structure.md`, with standalone `quantx-core` and `quantx-registry`. The resolution is recorded in `docs/DECISIONS.md` as D-001.
- **`00-index.md` bookkeeping gap.** `00-index.md`'s doc-set table does not list `14-directory-structure.md`, and its Change log is empty despite the SR-register renumbering (the old C1/M1-style scheme to `SR-1`..`SR-15`) and the addition of two docs — both changes `00-index.md`'s own stated rule says should be logged there. This is treated as a gap in `00-index.md`'s own bookkeeping, not as a signal that `14-directory-structure.md` is somehow less authoritative; `14` is followed throughout regardless.

## 4. Originally missing doc (resolved by the builder-readiness revision)

`QuantX-v2-Architecture.md`, referenced by both `06-system-architecture.md` and `03-user-stories-and-flows.md`, was not provided in the original upload. The builder-readiness revision created `docs/QUANTX-V2-ARCHITECTURE.md` as a versioned replacement and recorded that decision as D-005. The inference inventory below remains a historical record of the pre-revision scaffold; resolved wire-format entries are superseded by the replacement contract.

## 5. Every `(inferred)` marker used in the original generation pass (43 occurrences)

Collected here per `AI_AGENT_GUIDELINES.md` §5. Each was a genuine remaining gap after consulting all 15 docs — sound engineering judgment consistent with the docs, never presented with the same confidence as a sourced fact. Grouped by file:

- **`packages/quantx-authenticator/src/quantx_authenticator/hotp_provider.py.md`**
  - …ory-structure.md gives HOTP its own file separate from totp_provider.py — the docs establish both algorithms are in scope but describe their required behavior jointly, not HOTP's counter-increment specifics individually)
  - …py`'s `(inferred)
  - …e counter-based variant) `(inferred: FR-5.2 names TOTP explicitly; extending the same independent-rate-limiter discipline to HOTP is consistent with the architecture's general principle but not spelled out per-algorithm)
  - …- *(inferred)
- **`packages/quantx-authenticator/src/quantx_authenticator/push_authenticator.py.md`**
  - …bool` - **Outside:** Actually delivering the push notification over a specific push provider/transport `(inferred: the docs specify issuance rate-limiting and consume-once semantics, not the transport integration itself)
- **`packages/quantx-combiners/src/quantx_combiners/kem/kem_combiner.py.md`**
  - …t bound into HKDF info for SR-7, but this file's own docstring is where the exact combination — e.g. concatenating both shared secrets as HKDF `ikm`, or deriving twice and combining — gets written at implementation time)
- **`packages/quantx-combiners/src/quantx_combiners/kem/kem_wire_format.py.md`**
  - …py` `(inferred exact byte layout — deferred to the still-missing `QuantX-v2-Architecture.md`, per `AI_AGENT_GUIDELINES.md` §1b)
- **`packages/quantx-combiners/src/quantx_combiners/signature/signature_combiner.py.md`**
  - …'s own docstring is where the exact combination logic, AND vs. some other rule, gets written at implementation time; AND is the only reading consistent with hybrid being a security upgrade rather than an OR-weakened one)
- **`packages/quantx-combiners/src/quantx_combiners/signature/signature_wire_format.py.md`**
  - …; that level of detail is deferred to `QuantX-v2-Architecture.md`, which is referenced by 06-system-architecture.md and 03-user-stories-and-flows.md but has not been provided in this doc set — AI_AGENT_GUIDELINES.md §1b)
- **`packages/quantx-compliance/src/quantx_compliance/compliance_report_generator.py.md`**
  - …py` (this package) - **Imported by:** Integrating-application/CLI reporting entry points `(inferred consumer)
- **`packages/quantx-compliance/src/quantx_compliance/crypto_bom_model.py.md`**
  - …hed to output; whether that's a per-finding field or a report-level banner is left to implementation, but a per-finding field is the reading most consistent with SR-15's own wording, "attached to any output it produces")
- **`packages/quantx-compliance/src/quantx_compliance/standards_catalog.py.md`**
  - …erences, as static reference data `(inferred exact standards covered — the docs establish that a standards catalog exists and is consulted by the report generator, not which specific standards bodies/documents it covers)
- **`packages/quantx-core/src/quantx_core/exceptions/backend_unavailable_error.py.md`**
  - …- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)
- **`packages/quantx-core/src/quantx_core/exceptions/malformed_input_error.py.md`**
  - …py` (Layer 2, at the raw parsing stage, before a `Verifier`/`KEMProvider` is ever called) `(inferred: FR-0.1 is explicit that Verifier.verify()
  - …- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)
- **`packages/quantx-core/src/quantx_core/exceptions/rate_limited_error.py.md`**
  - …- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)
- **`packages/quantx-core/src/quantx_core/exceptions/replay_detected_error.py.md`**
  - …- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)
- **`packages/quantx-core/src/quantx_core/impls/in_memory_kv_store.py.md`**
  - …expire — enforced via explicit expiry check against the injected `Clock`, since there's no background eviction process in a plain in-memory dict `(inferred: 07-database-design.md states "explicit expiry check (in-memory)
- **`packages/quantx-core/src/quantx_core/impls/in_memory_rate_limiter.py.md`**
  - …nts `allow(identity_key) -> bool` over a sliding/fixed window counter `(inferred exact windowing algorithm — 07-database-design.md names `window_start`/`count` as the logical fields but doesn't mandate sliding vs. fixed)
  - …2/P5, rather than a private dict `(inferred, same reasoning as `in_memory_replay_store.py`)
- **`packages/quantx-core/src/quantx_core/impls/in_memory_replay_store.py.md`**
  - …ts own ad hoc dict/cache for anything that must survive across calls; the docs don't spell out InMemoryReplayStore's internal storage mechanism by name, but P5 make a private dict here inconsistent with the architecture)
- **`packages/quantx-core/src/quantx_core/impls/redis_kv_store.py.md`**
  - … a generic 500 (SR-4) `(inferred: the docs require this decision be made and documented; they don't dictate fail-closed vs. degrade as the specific choice — this file's own docstring is where that decision gets recorded)
- **`packages/quantx-core/src/quantx_core/types/algorithm_id.py.md`**
  - … `ED25519`, `ECDSA_P256`, `ML_DSA_65`, `ML_DSA_87`, `SLH_DSA`, `X25519`, `ML_KEM_768`, `ML_KEM_1024` `(inferred exact member names — the docs establish the eight algorithms in FR-1.2 but not this file's literal spelling)
- **`packages/quantx-core/src/quantx_core/types/ttl.py.md`**
  - …SR-14) `(inferred: this file defines the duration shape; the docs don't spell out whether expiry-math is a method on TTL or done by the caller, but SR-14 rules out this type reading wall-clock time internally either way)
- **`packages/quantx-crypto-adapters/src/quantx_crypto_adapters/classical/x25519_adapter.py.md`**
  - …this adapter presents it through the same encapsulate/decapsulate shape as the true KEMs so `KEMCombiner` can treat all Layer-1 KEM-side adapters uniformly; the docs establish X25519 as one of the eight adapters (FR-1.2)
- **`packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/ml_dsa_65_adapter.py.md`**
  - …md`) `(inferred: that doc gives this as an illustrative figure, not a hard spec this file must exactly match)
- **`packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/ml_kem_768_adapter.py.md`**
  - …md`) `(inferred illustrative figure, not an exact spec)
- **`packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/slh_dsa_adapter.py.md`**
  - …signature (hash-based signatures are typically larger than lattice-based ML-DSA `(inferred — the docs don't give SLH-DSA's specific size, only ML-DSA-65's ~3.3KB and ML-KEM-768's ~1.1KB as the budget's reference figures)
- **`packages/quantx-registry/config/algorithm_registry.example.yaml.md`**
  - …`session-auth` (HYBRID) and `session-auth-pqc-only` (PQC_ONLY) `(inferred exact role names — 04-functional-requirements.md names `session-auth` and `session-auth-pqc-only` as examples, not a mandated final list)
- **`packages/quantx-threshold/src/quantx_threshold/threshold_policy.py.md`**
  - …`m > n`) `(inferred: the docs specify duplicate-key rejection explicitly; an m > n bound check is an obvious corollary the docs don't spell out by name)
- **`packages/quantx-wallet/src/quantx_wallet/backup_code_manager.py.md`**
  - …`(inferred: the docs specify verification/consumption behavior, not the generation-and-delivery flow, which is presumably an integrating-application concern much like identity binding is per 09-auth-and-authorization.md)
- **`packages/quantx-wallet/src/quantx_wallet/device_linker.py.md`**
  - …erion: "device-pairing tokens can't be replayed") `(inferred detailed behavior — the docs establish device pairing as a Layer-7 recovery concern and its consume-once requirement, but not the exact pairing protocol shape)
  - …ring_token(subject_id) -> str`; `consume_pairing_token(token) -> bool` `(inferred exact method names — 02-build-order.md establishes the capability, "device-pairing tokens can't be replayed," not the literal API surface)
  - …## Security notes - *(inferred)
- **`packages/quantx-wallet/src/quantx_wallet/vault_metadata.py.md`**
  - …- `rotation_state` — the key's rotation status `(inferred exact value set — 07-database-design.md names `rotation_state` as a field but doesn't enumerate its possible values)
- **`packages/quantx-zkp/src/quantx_zkp/anonymous_proof_backend.py.md`**
  - …s raises NotImplementedError until funded, scoped external audit; the exact method names a real implementation would eventually have are deferred, per AI_AGENT_GUIDELINES.md §1b, to the missing QuantX-v2-Architecture.md)
- **`packages/quantx-zkp/src/quantx_zkp/merkle_membership_proof.py.md`**
  - …py` (this package) - **Imported by:** Any surface presenting a membership proof to a relying party (integrating-application concern) `(inferred consumer)
- **`packages/quantx-zkp/src/quantx_zkp/merkle_tree.py.md`**
  - …## Part of / dependency graph - **Package:** `quantx-zkp`, `src/quantx_zkp` - **Depends on:** A standard hash function (`(inferred)
- **`service/src/quantx_service/auth/bearer_token_auth.py.md`**
  - …omparison uses a constant-time comparison to avoid a timing side-channel `(inferred: standard practice for token comparison; the docs establish bearer-token auth as the mechanism, not this specific implementation detail)
- **`service/src/quantx_service/auth/mtls_auth.py.md`**
  - …py` — a deployment picks one per its own TLS termination setup, not both simultaneously `(inferred: the docs don't specify whether both can be enabled at once)
- **`service/src/quantx_service/config.py.md`**
  - … file — which recipe (A/B/C) to wire, backend connection details, TLS enforcement mode, rate-limit thresholds `(inferred exact config schema — the docs establish that config drives wiring, not this file's precise schema)
- **`service/src/quantx_service/middleware/hybrid_tls_enforcement.py.md`**
  - … TLS termination visibility allows it `(inferred: exact mechanism depends on where TLS terminates relative to this middleware — the docs establish the requirement (08-api-specification.md's required hybrid TLS 1.3 group)
- **`tools/softhsm2/setup_softhsm2_dev_token.sh.md`**
  - …- Idempotent — safe to re-run without duplicating tokens `(inferred: standard practice for a setup script; not explicitly required by the docs)

## 6. Judgment calls made without a directly-quotable source

Beyond the inline `(inferred)` markers above, these structural decisions were needed to complete the manifest and aren't individually flagged inline everywhere they recur:

- **Schema for non-`.py` root/config/CI/ADR files.** `BUILD_PROMPT.md` §3/§3a/§4 define schemas for `<name>.py.md` components, value types, and folder `README.md`s, but the manifest also calls for `.md` specs of `pyproject.toml`, `Dockerfile`, `.pre-commit-config.yaml`, the two GitHub Actions workflow files, `algorithm_registry.example.yaml`, the three `tools/lint/` scripts, the two `tools/softhsm2/`/`tools/fuzzing/` scripts, and the six `docs/adr/*.md` files. For these, this scaffold used a fourth, adapted schema (Purpose / Required contents or behavior / Non-negotiable principles / Source docs) that preserves the spirit of §3's traceability requirement without forcing fields (`Layer`, `Docstring contract`) that don't apply to a YAML/shell/CI file.
- **Exceptions and test files got the full §3 schema, not §3a.** `AI_AGENT_GUIDELINES.md` §6 names the specific value-type files that get the lighter §3a schema (`mode.py`, `challenge_record.py`, `session_token.py`, `vault_metadata.py`, `approval_record.py`, `push_approval_record.py`, `registry_role.py`) and doesn't mention exception classes or test files either way. This scaffold read that list as exhaustive for §3a and gave every exception class and every test file the full §3 schema, adapting the `Mandatory tests this must pass` section for test files themselves (since a test file doesn't have tests of its own to pass) to instead state plainly that the file *is* the test for the behavior/SR item it names.
- **One ADR file per gated *component group*, not per individual gated file.** `BUILD_PROMPT.md` §5's gate-review notice text names a single `docs/adr/<file>.md` shared by multiple related gated files (e.g. both `signature_combiner.py` and `signature_mode_enforcement.py` point at `signature_combiner.md`), which this scaffold followed literally rather than creating a separate ADR per file.
- **HOTP given its own file with TOTP-equivalent rate-limiting discipline extended by analogy.** `06-system-architecture.md` and `00-index.md` (D4) discuss "TOTP/HOTP" jointly as one second-factor concept, while `14-directory-structure.md` lists `hotp_provider.py` as a separate file from `totp_provider.py`. `07-database-design.md`'s TOTP/HOTP secret entity gave HOTP's counter-increment behavior directly; FR-5.2's independent-rate-limiter requirement names TOTP specifically and was extended to HOTP by analogy, flagged inline as `(inferred)`.

## 7. Self-check results (`AI_AGENT_GUIDELINES.md` §4)

1. **Path audit.** Zero missing, zero extra against `BUILD_PROMPT.md` §6's manifest — see §1 above.
2. **Citation audit.** Every `FR-x.y` and `SR-x` ID cited in this scaffold was checked against the actual register in `04-functional-requirements.md` / `10-security-requirements.md` while drafting the corresponding file, rather than against a remembered paraphrase; the two files were read in full before any citing file was written.
3. **Cross-file consistency audit.** Spot-checked recurring facts across packages: the `wallet_backend_interface.py` Protocol shape is described identically in `key_wallet.py.md`, each of the three backend files, and `backends/README.md`; SR-1's "mode fixed at construction, never from wire" wording is consistent across `signature_combiner.py.md`, `signature_mode_enforcement.py.md`, `challenge_issuer.py.md`, `session_orchestrator.py.md`, and `verify_router.py.md`; the dependency direction "depends only on lower layers, never sideways or up" is stated consistently in every package-level `README.md`.
4. **Schema audit.** Automated: all 170 `full`-schema files were checked programmatically for the presence of all eleven required §3 section headers, in order — 0 failures.
5. **Gate-review granularity check.** Confirmed the gate-review notice appears on exactly the 12 files `BUILD_PROMPT.md` §5 names (listed in §1 above) and not on the plumbing files that sit next to them — `signature_wire_format.py.md` and `kem_wire_format.py.md` explicitly state in their own Security notes section that they are *not* `GATE_REVIEW_REQUIRED`, precisely because past drafts of this kind of scaffold tend to over-apply the gate notice to everything in a sensitive-looking folder.

## 8. Explicit confirmation

No `GATE_REVIEW_REQUIRED` file, anywhere in this scaffold, is described as production-ready, audited, secure, or reviewed. Every one of the 12 gated files' `Status` line reads "pre-implementation — this is the spec for a file that does not exist yet," every one carries the literal `GATE_REVIEW_REQUIRED` notice text from `BUILD_PROMPT.md` §5 pointing at an `UNREVIEWED`, empty-sign-off-log ADR file, and the root `README.md` states plainly that this repository, at doc-generation time, is a specification scaffold rather than a built, reviewed system.

## 9. Scope boundary honored (`AI_AGENT_GUIDELINES.md` §7)

This pass produced documentation-scaffold `.md` files only — no `.py` implementation code was written and no dependencies were installed. The foundational docs were treated as source material; the architecture document was deliberately corrected during the builder-readiness revision, and the change is recorded above and in `docs/DECISIONS.md`.

## 10. AI-builder readiness revision

This scaffold was revised after the original documentation-only generation pass. The revision added `BUILD_INSTRUCTIONS.md` as the authoritative implementation contract and `AI_BUILDER_HANDOFF.md` as the concise handoff document. The revision explicitly defines the conversion from specification files such as `module.py.md` to target files such as `module.py`, preserves all specifications, establishes document precedence, defines the layer-by-layer validation sequence, and prohibits unsupported production or security claims.

The repository tree in `docs/06-system-architecture.md` was corrected to match `docs/14-directory-structure.md`: `quantx-core` is the standalone Layer 0 package and `quantx-registry` is the standalone Layer 3 package. The prior eight-package tree was stale and has been removed from the architecture reference. The root README specification now points builders to the two handoff documents.

The package remains intentionally non-runnable until an AI builder creates the target source, test, configuration, CI, and script files according to `BUILD_INSTRUCTIONS.md`. No implementation or dependency claim is implied by this revision.

## 11. Stricter completeness audit

The follow-up audit found that the original scaffold could not honestly be called contradiction-free or complete as an executable specification. The missing architecture source has now been replaced by `docs/QUANTX-V2-ARCHITECTURE.md`. Some target specifications still retain material `(inferred)` or `not specified` markers affecting fixtures, service implementation details, and cryptographic review obligations. `SPEC_COMPLETENESS_AUDIT.md` records the remaining findings and the minimum gate required before the documentation can be called complete. The AI-builder status remains conditional, not unconditional.
