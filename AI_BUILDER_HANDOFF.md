# QuantX AI-Builder Handoff

## Handoff status

This package is **conditionally ready for an AI coding builder to begin controlled implementation**, provided the builder follows `BUILD_INSTRUCTIONS.md` and `SPEC_COMPLETENESS_AUDIT.md`. It is not a runnable implementation yet, and it is not a complete executable specification. It is a traceable requirements scaffold with canonical architecture, security controls, tests to be created, and explicit review gates.

The distinction is intentional:

> Ready for implementation does not mean implemented, tested, audited, or production-ready.

## What the builder receives

The package contains the product requirements, user flows, functional requirements, non-functional requirements, architecture, database model, API contract, authorization model, multi-tenancy model, analytics/events, edge cases, security register, canonical directory structure, package specifications, test specifications, tool specifications, and ADR placeholders.

The package also contains `BUILD_INSTRUCTIONS.md`, which resolves the previously implicit question of how a builder should convert files such as `module.py.md` into `module.py` without damaging the source specifications. `SPEC_COMPLETENESS_AUDIT.md` records the material gaps that must be resolved before the specification can be called complete.

## Canonical decisions made for this handoff

| Decision | Resolution |
|---|---|
| Repository layout | `docs/14-directory-structure.md` is canonical. It separates `quantx-core` as Layer 0 and `quantx-registry` as Layer 3. |
| Architecture layout conflict | The older eight-package tree in `docs/06-system-architecture.md` has been replaced with the canonical ten-package tree. |
| Versioned architecture contract | `docs/QUANTX-V2-ARCHITECTURE.md` is the implementation authority for foundational interfaces, mode identifiers, wire formats, session sequence, service boundaries, and minimum golden vectors. |
| Source/spec relationship | Specification files remain in place. The builder creates target files by removing only the final `.md` suffix for paths explicitly identified by `BUILD_INSTRUCTIONS.md`. |
| PQC backend | `liboqs` is replaced by `cryptography` (pyca) `>=48,<51` for ML-KEM and ML-DSA (D-006 accepted, D-010 pin policy). `cryptography` verifies and does public-key work; production private keys stay in an HSM or KMS (D-008). SLH-DSA is blocked; no substitute library. |
| Anonymous proofs | `AnonymousProofBackend` remains interface-only until a vetted construction and independent review are available. |
| HSM testing | `HsmPkcs11Backend` must use SoftHSM2 or another real PKCS#11 implementation for development and tests. |
| Delivery | The framework is private. Clients receive generated source slices only (D-011). Backends are chosen by one `quantx.yaml` that fails closed (D-012). Only the sidecar is containerized (D-013). `FINAL_PLAN.md` is the one-page plan. |
| Open items | Decisions D-007 to D-017 are accepted (`docs/DECISIONS.md`). Still open: the `rotation_state` value set and AAD field list (`vault_metadata.py`), golden vectors, vendor-claim verification (S-016), the Python TLS group check (S-017), lawyer and independent review. Marker-level inferences are sorted in `docs/INFERENCE_TRIAGE.md`. |
| Production claims | No production, audit, security, or review claim is permitted without the evidence required by the security and ADR documents. |
| Validation | The builder must run tests, security tests, linting, formatting, strict type checking, and import-boundary checks after each layer. |
| Completeness status | Conditional only. The central architecture and wire-format gap is closed, but fixture completion, remaining API/service details, implementation evidence, and independent security review are still required. |

## Recommended builder prompt

Use the following instruction when starting the implementation:

> Read `BUILD_INSTRUCTIONS.md`, `AI_BUILDER_HANDOFF.md`, `SPEC_COMPLETENESS_AUDIT.md` and `docs/INFERENCE_TRIAGE.md` first. Treat `docs/14-directory-structure.md` as the canonical tree and `docs/10-security-requirements.md` as the security authority. This repository is a documentation-only scaffold. Create implementation files from the documented `*.md` specifications without deleting or overwriting the specifications. Implement in the order in `docs/02-build-order.md`, validate each layer, preserve all security requirements, and stop at any MUST-DECIDE file or open decision (D-007, D-008, D-009) and report it rather than guessing or weakening behavior. Do not claim that any component is production-ready, audited, secure, or reviewed without the required test evidence and independent sign-off. Keep `AnonymousProofBackend` as an interface only unless a vetted implementation and qualified reviewer are supplied.

## Acceptance criteria for the builder

The implementation is acceptable for a first engineering review when the builder has created the canonical directory structure, generated actual package metadata, implemented Layer 0 (except files awaiting a decision), passed its tests and checks, recorded all unresolved decisions, and produced an implementation-status report. The entire system is acceptable only after every layer, applicable security test, integration path, review gate, deployment requirement, and specification-completeness item has been completed.

## References

[0]: docs/INFERENCE_TRIAGE.md "QuantX inference triage"
[1]: BUILD_INSTRUCTIONS.md "QuantX AI-builder implementation contract"
[2]: docs/02-build-order.md "QuantX build order"
[3]: docs/10-security-requirements.md "QuantX security requirements"
[4]: docs/14-directory-structure.md "QuantX canonical directory structure"
