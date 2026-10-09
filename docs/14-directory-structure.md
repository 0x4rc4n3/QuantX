# QuantX — Directory Structure (Atomic Edition)

**Status:** Pre-implementation · **Depends on:** `06-system-architecture.md` (layers/components), `10-security-requirements.md` (SR register), `02-build-order.md` (build sequence). This doc is the literal, ready-to-scaffold tree — the previous docs say *what* and *when*; this says *where, as one small file per thing*.

## Why this shape

An AI coding agent works best when it can open one file, understand its entire job from the docstring alone, change it, and close it — never holding half a dozen unrelated concerns in context at once. So the rule here is stricter than "one class per file" (already required in `06-system-architecture.md`): **one class, one exception type, one value type, one backend, or one test unit per file, no exceptions.** A component that used to live as "the KeyWallet module" now lives as a folder: the orchestrating class in one file, each backend in its own file, the metadata type in its own file. Nothing here changes what gets built (`02-build-order.md` still governs that) — only how finely it's split on disk.

**Security tests get their own naming convention, on purpose.** Every test that directly verifies one entry in the security requirements register (`10-security-requirements.md`) is named `test_sr_<NN>_<slug>.py` — so "where's the test for SR-7" is a filename, not a search. Not every mandatory test maps to a numbered SR item (replay rejection and rate-limit rejection are foundational and cross-cutting rather than tied to one register entry, and wire-parser fuzzing is its own mandatory test category) — those get descriptive names instead, without a forced SR number.

## Ground rules

- Package directory names: kebab-case (`quantx-core`) — these are the publishable distribution names. Importable module names inside: snake_case (`quantx_core`) — standard Python.
- File names: snake_case, one file = one responsibility, filename describes exactly what's inside (`ed25519_adapter.py`, not `adapters.py`).
- Every package gets: `pyproject.toml`, `README.md` (states scope in one paragraph; carries the PQC backend statement if it touches PQC — `10-security-requirements.md`), `src/<module>/py.typed`, `tests/conftest.py`.
- Every package's `tests/` mirrors `src/` folder-for-folder, plus a `security/` subfolder for anything that verifies an SR item or a mandatory test category.
- A package's own docstring contract (Layer, Depends on, Implements, Outside, Inside, Wire format, Security notes — `06-system-architecture.md`) is written per-file, not per-package — atomicity doesn't mean losing context, it means each small file carries its own.
- This revises the 8-package summary tree in `06-system-architecture.md`: Layer 0 now gets its own package (`quantx-core`, previously folded into crypto-adapters) and Layer 3 now gets its own package (`quantx-registry`, previously folded into session) — every package now maps to exactly one layer number, except 6–7, which the layer table itself already treats as one unit (key custody + recovery). `06-system-architecture.md`'s repo-structure section has been updated to match this, so the two docs don't disagree.

## Root

```
quantx/
├── pyproject.toml                     # workspace root
├── README.md
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── ci.yml                     # pytest + ruff + black + mypy --strict, every package
│       └── security-register.yml      # runs every tests/security/ folder; fails if any SR item has no test
├── packages/                          # see per-package sections below
│   ├── quantx-core/
│   ├── quantx-crypto-adapters/
│   ├── quantx-combiners/
│   ├── quantx-registry/
│   ├── quantx-session/
│   ├── quantx-authenticator/
│   ├── quantx-wallet/
│   ├── quantx-threshold/
│   ├── quantx-zkp/
│   └── quantx-compliance/
├── service/                           # REST sidecar
├── docs/
│   ├── 00-index.md
│   ├── 01-product-requirements.md
│   ├── 02-build-order.md
│   ├── 03-user-stories-and-flows.md
│   ├── 04-functional-requirements.md
│   ├── 05-non-functional-requirements.md
│   ├── 06-system-architecture.md
│   ├── 07-database-design.md
│   ├── 08-api-specification.md
│   ├── 09-auth-and-authorization.md
│   ├── 10-security-requirements.md
│   ├── 11-multi-tenancy-model.md
│   ├── 12-analytics-and-events.md
│   ├── 13-error-and-edge-cases.md
│   ├── 14-directory-structure.md      # this file
│   └── adr/                           # one file per GATE_REVIEW_REQUIRED sign-off / non-trivial decision
├── tools/
└── tests/
    └── security/                      # root-level, cross-package END-TO-END SR suite — one file per SR item
        ├── test_sr_01_end_to_end_hybrid_downgrade.py
        ├── test_sr_02_end_to_end_membership_proof.py
        ├── test_sr_03_end_to_end_kv_store_cap.py
        ├── test_sr_04_end_to_end_backend_failure.py
        ├── test_sr_05_end_to_end_push_rate_limit.py
        ├── test_sr_06_end_to_end_custody_backend_failure.py
        ├── test_sr_07_end_to_end_kem_substitution.py
        ├── test_sr_08_end_to_end_single_canonicalization_path.py
        ├── test_sr_09_end_to_end_vault_metadata_tamper.py
        ├── test_sr_10_end_to_end_token_minting_order.py
        ├── test_sr_11_end_to_end_replay_rejection.py
        ├── test_sr_12_end_to_end_threshold_duplicate_key.py
        ├── test_sr_13_end_to_end_tls_trust_tagging.py
        ├── test_sr_14_end_to_end_clock_injection.py
        └── test_sr_15_end_to_end_scanner_disclaimer.py
```

## `quantx-core` — Layer 0

```
packages/quantx-core/
├── pyproject.toml
├── README.md
├── src/quantx_core/
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── signer.py
│   │   ├── verifier.py
│   │   ├── kem_provider.py
│   │   ├── canonicalizer.py
│   │   ├── clock.py
│   │   ├── key_value_store.py
│   │   ├── replay_store.py
│   │   └── rate_limiter.py
│   ├── types/
│   │   ├── __init__.py
│   │   ├── mode.py                        # Mode enum: HYBRID / PQC_ONLY / CLASSICAL_ONLY
│   │   ├── algorithm_id.py
│   │   └── ttl.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── backend_unavailable_error.py
│   │   ├── replay_detected_error.py
│   │   ├── rate_limited_error.py
│   │   └── malformed_input_error.py
│   ├── impls/
│   │   ├── __init__.py
│   │   ├── in_memory_kv_store.py
│   │   ├── redis_kv_store.py               # networked backend, optional `redis` extra
│   │   ├── jcs_canonicalizer.py
│   │   ├── system_clock.py
│   │   ├── in_memory_replay_store.py
│   │   └── in_memory_rate_limiter.py
│   └── py.typed
└── tests/
    ├── conftest.py
    ├── impls/
    │   ├── test_in_memory_kv_store.py
    │   ├── test_redis_kv_store.py
    │   ├── test_jcs_canonicalizer.py
    │   ├── test_system_clock.py
    │   ├── test_in_memory_replay_store.py
    │   └── test_in_memory_rate_limiter.py
    └── security/
        ├── test_sr_03_in_memory_max_entries_cap.py
        ├── test_sr_04_redis_backend_failure_handling.py
        └── test_sr_14_clock_never_defaults.py
```

## `quantx-crypto-adapters` — Layer 1

```
packages/quantx-crypto-adapters/
├── pyproject.toml
├── README.md                              # PQC backend statement required here (D-006)
├── src/quantx_crypto_adapters/
│   ├── __init__.py
│   ├── classical/
│   │   ├── __init__.py
│   │   ├── ed25519_adapter.py
│   │   ├── ecdsa_p256_adapter.py
│   │   └── x25519_adapter.py
│   ├── pqc/
│   │   ├── __init__.py
│   │   ├── ml_dsa_65_adapter.py
│   │   ├── ml_dsa_87_adapter.py
│   │   ├── slh_dsa_adapter.py              # spec only, blocked on pyca (D-006)
│   │   ├── ml_kem_768_adapter.py
│   │   └── ml_kem_1024_adapter.py
│   └── py.typed
└── tests/
    ├── conftest.py
    ├── classical/
    │   ├── test_ed25519_adapter.py
    │   ├── test_ecdsa_p256_adapter.py
    │   └── test_x25519_adapter.py
    ├── pqc/
    │   ├── test_ml_dsa_65_adapter.py
    │   ├── test_ml_dsa_87_adapter.py
    │   ├── test_slh_dsa_adapter.py         # spec only, blocked on pyca (D-006)
    │   ├── test_ml_kem_768_adapter.py
    │   └── test_ml_kem_1024_adapter.py
    └── security/
        └── test_verify_fails_closed_on_malformed_input.py   # FR-0.1, parametrized across every adapter
```

## `quantx-combiners` — Layer 2

The highest-stakes package (`GATE_REVIEW_REQUIRED`) — wire parsing, mode enforcement, and HKDF binding are each isolated so the security-critical logic is never mixed into the same file as encoding/decoding plumbing.

```
packages/quantx-combiners/
├── pyproject.toml
├── README.md
├── src/quantx_combiners/
│   ├── __init__.py
│   ├── signature/
│   │   ├── __init__.py
│   │   ├── signature_combiner.py          # public class — orchestrates only
│   │   ├── signature_wire_format.py       # encode/decode, length-prefixed parsing
│   │   └── signature_mode_enforcement.py  # required_mode cross-check, isolated (SR-1)
│   ├── kem/
│   │   ├── __init__.py
│   │   ├── kem_combiner.py                # public class — orchestrates only
│   │   ├── kem_wire_format.py              # encode/decode
│   │   └── kem_hkdf_binding.py             # ciphertext/pubkey → HKDF info binding (SR-7)
│   └── py.typed
└── tests/
    ├── conftest.py
    ├── signature/
    │   ├── test_signature_combiner.py
    │   └── test_signature_wire_format.py
    ├── kem/
    │   ├── test_kem_combiner.py
    │   └── test_kem_wire_format.py
    └── security/
        ├── test_sr_01_hybrid_downgrade_rejected.py
        ├── test_sr_07_kem_ciphertext_pubkey_substitution_rejected.py
        ├── test_signature_wire_format_fuzz.py      # mandatory test 5, Hypothesis
        └── test_kem_wire_format_fuzz.py             # mandatory test 5, Hypothesis
```

## `quantx-registry` — Layer 3

```
packages/quantx-registry/
├── pyproject.toml
├── README.md
├── src/quantx_registry/
│   ├── __init__.py
│   ├── algorithm_registry.py              # the ONE file allowed to import every Layer-1 adapter (FR-3.1)
│   ├── registry_role.py                   # role → (pairing, required_mode) value type
│   ├── registry_config_loader.py          # yaml.safe_load only, never yaml.load
│   └── registry_config_signature.py       # sign / verify the config file itself
├── config/
│   └── algorithm_registry.example.yaml
└── tests/
    ├── conftest.py
    ├── test_algorithm_registry.py
    ├── test_registry_role.py
    ├── test_registry_config_loader.py
    ├── test_registry_config_signature.py
    └── security/
        └── test_unsigned_config_rejected_when_signing_required.py
```

## `quantx-session` — Layer 4

```
packages/quantx-session/
├── pyproject.toml
├── README.md
├── src/quantx_session/
│   ├── __init__.py
│   ├── challenge_issuer.py
│   ├── challenge_record.py                # Challenge value type
│   ├── session_orchestrator.py
│   ├── session_token.py                   # SessionToken value type
│   └── default_setup.py                   # Recipe-A wiring helper — default_setup()
└── tests/
    ├── conftest.py
    ├── test_challenge_issuer.py
    ├── test_session_orchestrator.py
    ├── test_default_setup_end_to_end_demo.py    # the default_setup → start → finish → validate demo
    └── security/
        ├── test_sr_10_token_never_minted_before_all_gates_pass.py
        └── test_replay_and_rate_limit_rejection.py   # FR-4.2 / FR-4.4, foundational, no single SR number
```

## `quantx-authenticator` — Layer 5

```
packages/quantx-authenticator/
├── pyproject.toml
├── README.md
├── src/quantx_authenticator/
│   ├── __init__.py
│   ├── totp_provider.py
│   ├── hotp_provider.py
│   ├── push_authenticator.py
│   └── push_approval_record.py            # pending/consumed push-approval value type
└── tests/
    ├── conftest.py
    ├── test_totp_provider.py
    ├── test_hotp_provider.py
    ├── test_push_authenticator.py
    └── security/
        ├── test_totp_rate_limiter_independent_of_session_limiter.py   # FR-5.2
        ├── test_sr_05_push_issuance_rate_limited_before_send.py
        └── test_sr_11_push_approval_replay_rejected.py
```

## `quantx-wallet` — Layers 6–7

```
packages/quantx-wallet/
├── pyproject.toml
├── README.md
├── src/quantx_wallet/
│   ├── __init__.py
│   ├── key_wallet.py                      # public class — delegates to a backend, no storage logic itself
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── wallet_backend_interface.py    # shared Protocol every backend implements
│   │   ├── encrypted_file_backend.py
│   │   ├── os_keychain_backend.py
│   │   ├── hsm_pkcs11_backend.py          # PKCS#11 3.x; SoftHSM2 covers classical keys only, PQC needs SoftHSMv3/kryoptic (D-008)
│   │   ├── aws_kms_backend.py
│   │   └── gcp_kms_backend.py
│   ├── vault_metadata.py                  # value type, included in AEAD AAD
│   ├── backup_code_manager.py
│   └── device_linker.py
└── tests/
    ├── conftest.py
    ├── test_key_wallet.py
    ├── backends/
    │   ├── test_encrypted_file_backend.py
    │   ├── test_os_keychain_backend.py
    │   ├── test_hsm_pkcs11_backend.py     # classical keys on the SoftHSM2 dev token from tools/softhsm2/; PQC needs SoftHSMv3/kryoptic
    │   ├── test_aws_kms_backend.py
    │   └── test_gcp_kms_backend.py
    ├── test_backup_code_manager.py
    ├── test_device_linker.py
    └── security/
        ├── test_sr_09_vault_metadata_aad_authenticated.py
        ├── test_vault_corruption_raises_not_silent_empty.py
        ├── test_sr_06_backend_unavailable_raises_explicit_error.py
        └── test_sr_11_backup_code_replay_rejected.py
```

## `quantx-threshold` — Layer 8

```
packages/quantx-threshold/
├── pyproject.toml
├── README.md
├── src/quantx_threshold/
│   ├── __init__.py
│   ├── threshold_policy.py
│   ├── threshold_manager.py
│   └── approval_record.py                 # one signature toward quorum, value type
└── tests/
    ├── conftest.py
    ├── test_threshold_policy.py
    ├── test_threshold_manager.py
    └── security/
        └── test_sr_12_duplicate_key_rejected_at_policy_creation.py
```

## `quantx-zkp` — Layer 9

```
packages/quantx-zkp/
├── pyproject.toml
├── README.md                              # non-anonymity caveat required here (FR-9.3)
├── src/quantx_zkp/
│   ├── __init__.py
│   ├── merkle_tree.py                     # tree construction, isolated from proof verification
│   ├── merkle_membership_proof.py
│   └── anonymous_proof_backend.py         # Protocol only — NotImplementedError body, no logic
└── tests/
    ├── conftest.py
    ├── test_merkle_tree.py
    ├── test_merkle_membership_proof.py
    ├── test_anonymous_proof_backend_raises_not_implemented.py
    └── security/
        └── test_sr_02_merkle_proof_actually_walks_path_to_root.py
```

## `quantx-compliance` — Layer 10

```
packages/quantx-compliance/
├── pyproject.toml
├── README.md
├── src/quantx_compliance/
│   ├── __init__.py
│   ├── crypto_bom_model.py
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── static_source_scanner.py
│   │   └── tls_inspector.py
│   ├── standards_catalog.py
│   └── compliance_report_generator.py
└── tests/
    ├── conftest.py
    ├── test_crypto_bom_model.py
    ├── scanners/
    │   ├── test_static_source_scanner.py
    │   └── test_tls_inspector.py
    ├── test_standards_catalog.py
    ├── test_compliance_report_generator.py
    └── security/
        ├── test_sr_13_tls_findings_tagged_by_trust_level.py
        └── test_sr_15_scanner_disclaimer_attached_to_output.py
```

## `service` — REST sidecar

```
service/
├── pyproject.toml
├── Dockerfile
├── src/quantx_service/
│   ├── __init__.py
│   ├── main.py                            # app factory / entrypoint ONLY — no logic
│   ├── config.py                          # quantx.yaml schema, loader, validator (docs/15)
│   ├── cli.py                             # quantx init/validate/explain/run, thin
│   ├── wiring.py                          # composes the SDK packages into the running app
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── challenge_router.py            # POST /v1/challenge
│   │   ├── verify_router.py               # POST /v1/verify
│   │   └── session_router.py              # GET /v1/session/:id
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── bearer_token_auth.py
│   │   └── mtls_auth.py
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── error_envelope.py
│   │   ├── malformed_request_error.py
│   │   ├── verification_failed_error.py
│   │   ├── not_found_error.py
│   │   ├── already_consumed_error.py
│   │   ├── rate_limited_error.py
│   │   └── backend_unavailable_error.py
│   └── middleware/
│       ├── __init__.py
│       ├── hybrid_tls_enforcement.py      # enforces the X25519MLKEM768 requirement (08-api-specification.md)
│       └── rate_limit_headers.py
└── tests/
    ├── conftest.py
    ├── test_cli.py
    ├── test_config_validation.py
    ├── routers/
    │   ├── test_challenge_router.py
    │   ├── test_verify_router.py
    │   └── test_session_router.py
    └── security/
        └── test_sr_01_sidecar_never_trusts_declared_mode.py
```

## `tools` — dev/CI helpers, not shipped

```
tools/
├── softhsm2/
│   └── setup_softhsm2_dev_token.sh        # unblocks HsmPkcs11Backend immediately, no client hardware needed
├── fuzzing/
│   └── run_all_wire_parser_fuzz_suites.sh
└── lint/
    ├── check_docstring_contract.py        # enforces FR-X.1 across every package
    ├── check_no_sibling_imports.py        # enforces FR-X.2 across every package
    └── check_single_canonicalization_path.py   # enforces SR-8 — fails if any file outside JCSCanonicalizer serializes-for-signing
```

## `factory/` — private, never delivered, never published (D-011)

```
factory/
├── slicer/        # config -> dependency closure -> file list
├── generator/     # frozen wiring, narrowed schema, build manifest
├── builder/       # quantx-builder.html, quantx-puzzle.html
├── release/       # lockfile, SBOM, image build and signing, patch rebuilds
└── tests/         # slice-leak, reproducibility and manifest tests
```

Contract: `docs/16-delivery-and-factory.md`. File-level specs follow the one-file-one-job convention and are written when build step 12 starts. `factory/` is excluded from every delivered slice and from every package.

## File-count sanity check

This is intentionally a lot of files — that's the point. Every one of them is small enough to read start-to-finish in under a minute: Layer-1 adapters stay ~30–60 lines (`FR-1.3`), most other source files land in the same rough range, test files are unbounded but scoped to one unit. Nothing here adds new components beyond what `06-system-architecture.md` already lists — it's the same component set, just given room to breathe on disk instead of being bundled into fewer, larger files.
