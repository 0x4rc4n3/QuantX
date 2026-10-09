# QuantX Inference Triage

**Purpose.** `SPEC_COMPLETENESS_AUDIT.md` S-006 and the builder's hard-stop rule treat every `(inferred)`, `not specified`, `unresolved`, `TBD` or `deferred` marker as a stop. Most are harmless. This file sorts them so the builder knows which ones really stop work and the owner knows which decisions to make first.

**Scope.** 132 marker lines remain by keyword match across the spec tree on 2026-10-03 (158 before the first triage; the D-007 to D-016 decisions then cleared the rest of the must-decide rows except one), excluding the meta documents (`GENERATION_REPORT.md`, `SPEC_COMPLETENESS_AUDIT.md`, `BUILD_INSTRUCTIONS.md`, `AI_BUILDER_HANDOFF.md`, `docs/DECISIONS.md`, this file). It is a keyword count, so it is a floor: it cannot find a gap nobody marked.

## Classes

| Class | Meaning | Hard stop? | Marker lines |
|---|---|---|---|
| RESOLVED | Closed by `QUANTX-V2-ARCHITECTURE.md`, D-006 or a verified fact | No | 12 (4 markers removed, 2 still present but decided) |
| MUST-DECIDE | Affects crypto, wire, persistence or deployment behavior; needs an accepted entry in `docs/DECISIONS.md` first | **Yes, for that file only** | 1 lines in 1 files |
| ACCEPT | Low-risk inference (error attribute shapes, consumers, naming, empty edge-case section). Builder proceeds and records any behavior it settles | No | 52 |
| FIXTURE-VECTORS | Test spec whose expected values must come from golden vectors (S-002, S-005) | Yes, for the expected values | 24 |
| FIXTURE-BUILDER | Test spec whose fixtures the builder can write from the source spec | No | 48 |
| OPEN-BY-DESIGN | Deliberately open (D8 latency targets) | No | 1 |
| NOT-A-MARKER | Keyword matched ordinary prose | No | 4 |

## MUST-DECIDE, grouped by the layer that needs them

Proposed defaults are suggestions for the owner to accept or change. They are not decisions, and the builder must not apply them until they are logged as accepted. Each accepted default becomes its own `D-011+` entry.

| Needed by | File | What must be decided | Proposed default |
|---|---|---|---|
| Layer 6-7 | `packages/quantx-wallet/src/quantx_wallet/vault_metadata.py.md` | `rotation_state` value set and the exact AAD field list (the key_format values are accepted in D-007) | Propose: rotation_state in {active, retired, revoked}; AAD = key_id, key_format, algorithm, created_at, rotation_state |

Also required, tracked as decisions rather than markers: **D-007** (vault key format, before Layer 6), **D-008** (HSM and PQC key material, before the HSM backend), **D-009** (signature domain separation, before Layer 2 and the signature vectors).

## RESOLVED

| File | Note |
|---|---|
| `packages/quantx-authenticator (TOTP, HOTP, pyproject)` | Decided in D-015: RFC defaults, stdlib hmac, look-ahead 10, per-factor rate limiter. |
| `packages/quantx-wallet/src/quantx_wallet/device_linker.py.md` | Decided in D-015: 256-bit single-use token, 10-minute expiry, method names. |
| `packages/quantx-zkp/src/quantx_zkp/merkle_tree.py.md` | Decided in D-015: SHA-256, leaf/node prefixes, no last-leaf duplication. |
| `packages/quantx-core/src/quantx_core/impls/in_memory_rate_limiter.py.md` | Decided in D-015: fixed window. |
| `packages/quantx-crypto-adapters/.../x25519_adapter.py.md` | Decided in D-015: ephemeral-key KEM mapping. |
| `service/.../config.py.md, hybrid_tls_enforcement.py.md, mtls_auth.py.md` | Decided in D-016: the service terminates TLS, no proxy trust, one auth method only. |
| `packages/quantx-combiners/src/quantx_combiners/kem/kem_combiner.py.md` | HKDF construction is normative in V2 §7; marker removed. |
| `packages/quantx-combiners/src/quantx_combiners/signature/signature_combiner.py.md` | AND rule is normative in V2 §8; marker removed. Message construction still open (D-009). |
| `packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/ml_dsa_65_adapter.py.md` | Exact sizes 3,309 B signature / 1,952 B public key; marker removed. |
| `packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/ml_kem_768_adapter.py.md` | Exact sizes 1,088 B ciphertext / 1,184 B public key; marker removed. |
| `packages/quantx-core/src/quantx_core/types/algorithm_id.py.md` | Decided: `SLH_DSA` reserved, registry fails closed (D-006). Member spelling still marked inferred; accept. |
| `packages/quantx-crypto-adapters/src/quantx_crypto_adapters/pqc/slh_dsa_adapter.py.md` | Decided: blocked upstream, no substitute library (D-006). One size-estimate marker remains and is moot until unblocked. |

## ACCEPT

Builder may proceed. Summary by package (file:line):

- **quantx-authenticator** (2): `README.md`:21, `push_authenticator.py.md`:17
- **quantx-compliance** (7): `compliance_report_generator.py.md`:11, `compliance_report_generator.py.md`:27, `compliance_report_generator.py.md`:30, `crypto_bom_model.py.md`:15, `static_source_scanner.py.md`:30, `standards_catalog.py.md`:22, `standards_catalog.py.md`:30
- **quantx-core** (22): `backend_unavailable_error.py.md`:23, `backend_unavailable_error.py.md`:30, `malformed_input_error.py.md`:11, `malformed_input_error.py.md`:23, `malformed_input_error.py.md`:30, `rate_limited_error.py.md`:23, `rate_limited_error.py.md`:30, `replay_detected_error.py.md`:23, `replay_detected_error.py.md`:30, `in_memory_kv_store.py.md`:24, `in_memory_replay_store.py.md`:23, `jcs_canonicalizer.py.md`:32, `redis_kv_store.py.md`:23, `canonicalizer.py.md`:29, `clock.py.md`:29, `kem_provider.py.md`:29, `key_value_store.py.md`:29, `rate_limiter.py.md`:30, `replay_store.py.md`:30, `signer.py.md`:29, `verifier.py.md`:29, `ttl.py.md`:15
- **quantx-registry** (2): `algorithm_registry.example.yaml.md`:9, `registry_config_loader.py.md`:23
- **quantx-session** (1): `default_setup.py.md`:31
- **quantx-threshold** (2): `threshold_policy.py.md`:29, `threshold_policy.py.md`:35
- **quantx-wallet** (2): `wallet_backend_interface.py.md`:30, `backup_code_manager.py.md`:17
- **quantx-zkp** (2): `anonymous_proof_backend.py.md`:32, `merkle_membership_proof.py.md`:13
- **service** (11): `bearer_token_auth.py.md`:19, `bearer_token_auth.py.md`:30, `already_consumed_error.py.md`:30, `backend_unavailable_error.py.md`:30, `malformed_request_error.py.md`:30, `not_found_error.py.md`:30, `rate_limited_error.py.md`:30, `verification_failed_error.py.md`:30, `main.py.md`:30, `rate_limit_headers.py.md`:29, `wiring.py.md`:31
- **tools** (1): `setup_softhsm2_dev_token.sh.md`:11

Pattern notes: the repeated line "not specified in the available source docs — flag for human review" sits in an empty edge-case section of Layer-0 interface specs, exception classes and service error classes. It means nothing is required beyond the interface contract. Exception classes must not put secrets or raw untrusted input in messages (V2 §10).

## FIXTURE-VECTORS (expected values need golden vectors)

`packages/quantx-combiners/tests/conftest.py.md`:30, `packages/quantx-combiners/tests/kem/test_kem_combiner.py.md`:30, `packages/quantx-combiners/tests/kem/test_kem_wire_format.py.md`:30, `packages/quantx-combiners/tests/signature/test_signature_combiner.py.md`:31, `packages/quantx-combiners/tests/signature/test_signature_wire_format.py.md`:31, `packages/quantx-registry/tests/conftest.py.md`:29, `packages/quantx-registry/tests/security/test_unsigned_config_rejected_when_signing_required.py.md`:23, `packages/quantx-registry/tests/test_algorithm_registry.py.md`:31, `packages/quantx-registry/tests/test_registry_config_loader.py.md`:31, `packages/quantx-registry/tests/test_registry_config_signature.py.md`:31, `packages/quantx-registry/tests/test_registry_role.py.md`:30, `packages/quantx-threshold/tests/conftest.py.md`:29, `packages/quantx-threshold/tests/test_threshold_policy.py.md`:30, `packages/quantx-wallet/tests/backends/test_encrypted_file_backend.py.md`:30, `packages/quantx-wallet/tests/backends/test_hsm_pkcs11_backend.py.md`:30, `packages/quantx-wallet/tests/backends/test_os_keychain_backend.py.md`:30, `packages/quantx-zkp/tests/conftest.py.md`:29, `packages/quantx-zkp/tests/test_anonymous_proof_backend_raises_not_implemented.py.md`:29, `packages/quantx-zkp/tests/test_merkle_membership_proof.py.md`:30, `packages/quantx-zkp/tests/test_merkle_tree.py.md`:30, `tests/security/test_sr_01_end_to_end_hybrid_downgrade.py.md`:30, `tests/security/test_sr_07_end_to_end_kem_substitution.py.md`:30, `tests/security/test_sr_09_end_to_end_vault_metadata_tamper.py.md`:30, `tests/security/test_sr_12_end_to_end_threshold_duplicate_key.py.md`:30

## FIXTURE-BUILDER (builder may write)

`packages/quantx-authenticator/tests/conftest.py.md`:29, `packages/quantx-authenticator/tests/security/test_sr_05_push_issuance_rate_limited_before_send.py.md`:30, `packages/quantx-authenticator/tests/security/test_totp_rate_limiter_independent_of_session_limiter.py.md`:30, `packages/quantx-authenticator/tests/test_hotp_provider.py.md`:30, `packages/quantx-authenticator/tests/test_push_authenticator.py.md`:30, `packages/quantx-authenticator/tests/test_totp_provider.py.md`:30, `packages/quantx-compliance/tests/conftest.py.md`:29, `packages/quantx-compliance/tests/scanners/test_static_source_scanner.py.md`:29, `packages/quantx-compliance/tests/scanners/test_tls_inspector.py.md`:30, `packages/quantx-compliance/tests/security/test_sr_15_scanner_disclaimer_attached_to_output.py.md`:30, `packages/quantx-compliance/tests/test_compliance_report_generator.py.md`:30, `packages/quantx-compliance/tests/test_crypto_bom_model.py.md`:29, `packages/quantx-compliance/tests/test_standards_catalog.py.md`:29, `packages/quantx-core/tests/conftest.py.md`:30, `packages/quantx-core/tests/impls/test_in_memory_kv_store.py.md`:32, `packages/quantx-core/tests/impls/test_in_memory_rate_limiter.py.md`:31, `packages/quantx-core/tests/impls/test_in_memory_replay_store.py.md`:30, `packages/quantx-core/tests/impls/test_jcs_canonicalizer.py.md`:30, `packages/quantx-core/tests/impls/test_redis_kv_store.py.md`:31, `packages/quantx-core/tests/impls/test_system_clock.py.md`:30, `packages/quantx-core/tests/security/test_sr_03_in_memory_max_entries_cap.py.md`:31, `packages/quantx-core/tests/security/test_sr_04_redis_backend_failure_handling.py.md`:30, `packages/quantx-core/tests/security/test_sr_14_clock_never_defaults.py.md`:30, `packages/quantx-crypto-adapters/tests/conftest.py.md`:29, `packages/quantx-session/tests/conftest.py.md`:29, `packages/quantx-session/tests/test_challenge_issuer.py.md`:31, `packages/quantx-session/tests/test_default_setup_end_to_end_demo.py.md`:31, `packages/quantx-session/tests/test_session_orchestrator.py.md`:31, `packages/quantx-wallet/tests/conftest.py.md`:29, `packages/quantx-wallet/tests/test_backup_code_manager.py.md`:29, `packages/quantx-wallet/tests/test_device_linker.py.md`:30, `packages/quantx-wallet/tests/test_key_wallet.py.md`:30, `service/tests/conftest.py.md`:29, `service/tests/routers/test_challenge_router.py.md`:30, `service/tests/routers/test_session_router.py.md`:30, `service/tests/routers/test_verify_router.py.md`:31, `tests/conftest.py.md`:29, `tests/security/test_sr_02_end_to_end_membership_proof.py.md`:30, `tests/security/test_sr_03_end_to_end_kv_store_cap.py.md`:30, `tests/security/test_sr_04_end_to_end_backend_failure.py.md`:30, `tests/security/test_sr_05_end_to_end_push_rate_limit.py.md`:30, `tests/security/test_sr_06_end_to_end_custody_backend_failure.py.md`:30, `tests/security/test_sr_08_end_to_end_single_canonicalization_path.py.md`:30, `tests/security/test_sr_10_end_to_end_token_minting_order.py.md`:30, `tests/security/test_sr_11_end_to_end_replay_rejection.py.md`:30, `tests/security/test_sr_13_end_to_end_tls_trust_tagging.py.md`:30, `tests/security/test_sr_14_end_to_end_clock_injection.py.md`:30, `tests/security/test_sr_15_end_to_end_scanner_disclaimer.py.md`:30

## OPEN-BY-DESIGN and NOT-A-MARKER

`docs/05-non-functional-requirements.md`:51, `docs/00-index.md`:24, `docs/02-build-order.md`:3, `docs/05-non-functional-requirements.md`:16, `docs/README.md`:12

## How to use this file

1. The builder may implement every RESOLVED, ACCEPT and FIXTURE-BUILDER item without asking.
2. The builder stops at a MUST-DECIDE file until its decision is accepted in `docs/DECISIONS.md`, then continues with the rest of the layer.
3. When a decision is accepted, move the row to RESOLVED here and remove the marker from the spec file in the same commit.
