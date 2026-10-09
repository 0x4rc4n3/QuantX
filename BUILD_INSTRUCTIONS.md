# QuantX AI-Builder Implementation Contract

**Status:** Authoritative build instructions for converting this documentation scaffold into a runnable implementation.

## 1. Project status

This repository is a **documentation-only implementation scaffold**. It is not an existing application, library, or production security system. The files ending in `.md` that mirror source, test, configuration, CI, or script paths describe files that the builder must create. Do not claim that a component exists, works, is secure, audited, or production-ready until the corresponding implementation, tests, validation, and independent review are complete. Read `SPEC_COMPLETENESS_AUDIT.md` before implementation; it identifies known gaps that prevent a claim of a complete executable specification.

The builder must preserve the documented architecture and must stop with an explicit report when a requirement is ambiguous, contradictory, impossible to test, or dependent on unavailable hardware or an unevaluated cryptographic construction.

## 2. Authoritative document order

When two documents appear to disagree, resolve them in this order:

1. `BUILD_INSTRUCTIONS.md` for repository conversion and builder behavior.
2. `docs/14-directory-structure.md` for the canonical repository tree.
3. `docs/QUANTX-V2-ARCHITECTURE.md` for versioned public interfaces, wire formats, session sequencing, and reference sidecar boundaries.
4. `docs/10-security-requirements.md` for security requirements and required security tests.
5. `docs/04-functional-requirements.md` for functional behavior.
6. `docs/06-system-architecture.md` for layers, dependency direction, and composition.
7. `docs/02-build-order.md` for implementation sequencing.
8. The remaining documents for their stated subject matter.
9. Individual `*.md` file specifications for the target file they name, provided they do not violate items 1–8.

If a conflict cannot be resolved using this order, do not silently choose. Record it in `docs/DECISIONS.md`, explain the selected interpretation, and add or update a test when the decision affects behavior. If the unresolved choice affects public behavior, cryptographic behavior, persistence, deployment, or wire compatibility, stop implementation of that component until the decision is explicitly accepted.

## 3. File conversion rules

The builder must create target files from specification files using the following rules:

| Specification file | Target file | Conversion rule |
|---|---|---|
| `packages/**/src/**/*.py.md` | Same path with the final `.md` removed | Implement the described Python module. |
| `packages/**/tests/**/*.py.md` | Same path with the final `.md` removed | Implement the described test module. |
| `packages/**/pyproject.toml.md` | Same path with the final `.md` removed | Create the package metadata and pinned dependencies. |
| `service/**/*.py.md` | Same path with the final `.md` removed | Implement the service module. |
| `service/pyproject.toml.md` | `service/pyproject.toml` | Create service metadata. |
| `service/Dockerfile.md` | `service/Dockerfile` | Create the container definition. |
| `tools/**/*.py.md` | Same path with the final `.md` removed | Implement the tool. |
| `tools/**/*.sh.md` | Same path with the final `.md` removed | Implement the script with strict shell settings. |
| `*.yaml.md`, `*.yml.md`, `.pre-commit-config.yaml.md` | Same path with the final `.md` removed | Create the configuration file. |
| `docs/adr/*.md` | Same path | Keep as human-maintained ADRs; do not convert or overwrite them. |
| `docs/*.md`, `README.md`, `GENERATION_REPORT.md`, and package `README.md` files | Same path | Keep as documentation. Update only when a decision or implementation status requires it. |

Never rename or overwrite the specification files merely to make the project appear implemented. The generated source files and the specifications must coexist until the implementation is complete and reviewed.

## 4. Required implementation sequence

Implement and validate one layer at a time in the order defined by `docs/02-build-order.md`:

1. Layer 0: core interfaces and safe reference implementations.
2. Layer 1: classical and post-quantum algorithm adapters.
3. Layer 2: signature and KEM combiners.
4. Layer 3: algorithm registry and signed configuration.
5. Layer 4: challenge and session orchestration.
6. Layer 5: TOTP and push authentication.
7. Layers 6–7: key custody, backup codes, and device linking.
8. Layer 8: threshold governance.
9. Layer 9: Merkle membership proofs; keep `AnonymousProofBackend` as an interface only unless a vetted implementation and qualified independent review are available.
10. Layer 10: compliance and observability tooling.
11. Service sidecar and integration wiring as soon as its dependencies are available.
12. Configuration and CLI (`docs/15-config-and-composition.md`): the first version lands with Layer 4 and the sidecar.
13. Conformance suites, then the private factory (`docs/16-delivery-and-factory.md`). The factory is never packaged, published or delivered.

After each layer, run the applicable unit tests, security tests, linting, formatting, type checking, and import-boundary checks. Do not continue while a prior layer is failing unless the failure is documented as an explicitly approved temporary integration boundary.

## 5. Non-negotiable security behavior

The builder must implement every requirement in `docs/10-security-requirements.md`. In particular:

- Never accept the cryptographic mode from client or wire data.
- Fail closed on malformed or unverifiable cryptographic input.
- Bind KEM ciphertext and public key into the HKDF context.
- Use exactly one canonicalization path for signed data.
- Never silently fall back from HSM, OS keychain, or networked state storage to weaker storage.
- Authenticate vault metadata as AEAD associated data and raise on corruption.
- Mint a session token only after all required gates pass.
- Enforce replay protection and rate limits through the specified interfaces.
- Reject duplicate threshold keys during policy creation.
- Attach trust levels to TLS findings and disclaimers to static-analysis output.
- Use an injected `Clock`; never substitute wall-clock access through a fallback expression.
- Keep the PQC backend statement (D-006) attached to every artifact that references a PQC adapter.
- Declare `cryptography>=48,<51` in package metadata and install from an exact lockfile (D-010). Use Python 3.11+.
- Production private keys, classical and PQC, are HSM or KMS resident (D-008). `cryptography` verifies and does public-key work only; resident keys are used through `signer_for`/`decapsulator_for` and never returned (`KeyNotExportableError`). Software custody (D-007 seed format) is dev and staging only.
- Sign and verify the D-009 payload for every component, with ML-DSA `context=None`. TLS is terminated by the service itself (D-016).
- Never describe a backend as on-token PQC unless the provider reports PQC support for that algorithm. SoftHSM2 has none. Vendor claims in D-008 must be verified before a client is promised them.
- Never put `factory/` content into a package or a delivered slice, and never publish it. Config must fail closed, hold no secrets, and refuse blocked or interface-only options (D-011, D-012, D-014).
- Do not create `slh_dsa_adapter.py` or its test until D-006 is unblocked, and do not substitute another library for it.

Do not replace a security requirement with a comment, a mock, a constant result, a disabled test, or a weaker fallback.

## 6. Review gates and explicit non-goals

The following components require independent review before any production-readiness statement: signature and KEM combiners, the algorithm registry, all key-wallet backends, threshold policy/management, and membership-proof components. Record each review in the appropriate file under `docs/adr/`; an author cannot provide the independent sign-off.

`AnonymousProofBackend` must remain an interface-only component unless a specific vetted anonymous-membership scheme, implementation, test plan, and qualified reviewer are identified. An unaudited approximation is prohibited.

`HsmPkcs11Backend` must be developed and tested against SoftHSM2 or another real PKCS#11 module. A hardware device is not required for local development, but a fake backend must not be presented as HSM coverage.

## 7. Definition of done

A component is complete only when all of the following are true:

1. The target source file exists at the canonical path.
2. Its public behavior matches the applicable requirements and file specification.
3. Its docstring follows the required contract: Layer, Depends on, Implements, Outside, Inside, Wire format, and Security notes.
4. Unit tests and applicable security tests pass.
5. `ruff`, `black --check`, and `mypy --strict` pass for the affected package.
6. Import direction and dependency boundaries pass the custom lint checks.
7. Dependencies are pinned and no secret, private key, credential, or production configuration is committed.
8. Any required ADR and independent review record exists.
9. The implementation status is reflected in the relevant README and generation/build report.

The complete project is ready for an AI-builder handoff when the builder can execute the conversion rules without guessing, all contradictions are either resolved or recorded, and the repository contains a reproducible validation command.

## 8. First builder actions

Before implementing application logic, the builder must:

1. Read `docs/00-index.md` through `docs/14-directory-structure.md`, `docs/DECISIONS.md` and `docs/INFERENCE_TRIAGE.md`.
2. Inventory every `*.md` file that describes a target file.
3. Create the canonical directories and empty target paths.
4. Create the root and package metadata with exact dependency pins.
5. Create CI, pre-commit, and test configuration.
6. Implement Layer 0 and run its complete validation suite.
7. Produce a machine-readable or Markdown implementation-status report listing created files, tests run, failures, unresolved decisions, and review gates.

The builder must not generate a frontend, blockchain contract, trading engine, or unrelated feature unless a requirement document explicitly requests it. QuantX is an authentication and cryptographic-agility system, not a generic finance application.

## 9. Required validation command

Once the implementation files exist, the repository must provide a documented command equivalent to:

```bash
python -m pytest
ruff check .
black --check .
mypy --strict packages service tests
```

If a command is not applicable at an intermediate layer, the builder must state why and provide the narrower command that replaces it. A green result from only one of these tools is not sufficient evidence of readiness.

## 10. Completeness limitation

This scaffold is not certified as contradiction-free or complete. `SPEC_COMPLETENESS_AUDIT.md` lists unresolved wire-format, API, service-topology, fixture, dependency, and cryptographic-construction details. An AI builder may proceed with inventory, mechanical conversion, documentation, and clearly specified lower-risk work, but it must not invent or silently settle a material unresolved detail. “Take any kind of risk” is not an acceptable instruction for cryptographic foundations; unresolved material choices require an explicit decision, test vectors, and appropriate review.

## References

[1]: docs/02-build-order.md "QuantX build order"
[2]: docs/06-system-architecture.md "QuantX system architecture"
[3]: docs/10-security-requirements.md "QuantX security requirements"
[4]: docs/14-directory-structure.md "QuantX canonical directory structure"
[6]: docs/INFERENCE_TRIAGE.md "QuantX inference triage"
[5]: SPEC_COMPLETENESS_AUDIT.md "QuantX specification completeness audit"
