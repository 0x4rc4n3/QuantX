# QuantX: Final Plan

**Date:** 2026-10-04 · **Status:** All planned decisions D-001 to D-017 are accepted. The open items and gates below still stand. Nothing in this archive has been built, run or reviewed.

## What we are making

QuantX is a crypto-agile authentication engine that combines classical and post-quantum algorithms. The framework is made of small components that fit together through typed contracts, like puzzle pieces. A backend is not coded: it is chosen from a menu of parts in one `quantx.yaml` file, checked by one validator, and built from the company's private framework.

## How it makes money

Per-client migration consulting and custom composed authentication (D3). The company keeps the framework and its tooling private. Each client buys a generated source slice for their own configuration, which they can read in full, plus maintenance and review (D-011).

## The plan in one view

| Part | What it is | Where |
|---|---|---|
| Components | Layers 0 to 10, each behind a Layer 0 contract, wrapped around pyca for PQC | `docs/06`, `docs/14` |
| Wire contract | Container formats, HKDF binding, smoke vectors | `docs/QUANTX-V2-ARCHITECTURE.md` |
| Configuration | One `quantx.yaml`, one validator, fail closed, CLI | `docs/15`, D-012 |
| Containers | One hardened sidecar image; libraries stay libraries | D-013 |
| Factory (private) | Slicer, generator, builder, release pipeline | `docs/16`, D-011 |
| Builder UI | Puzzle configurator, exports the config format | `factory/builder/` |

## Decisions

| ID | Decision | Status |
|---|---|---|
| D-001 | Canonical package tree | Accepted |
| D-002 | Spec-to-source conversion rule | Accepted |
| D-003 | Anonymous proofs stay interface-only | Held by security rule |
| D-004 | SoftHSM2 as the HSM dev target | Accepted |
| D-005 | Replacement architecture contract | Accepted, independent review still required |
| D-006 | pyca replaces liboqs; SLH-DSA blocked | Accepted |
| D-007 | Software-custody key format (dev and staging) | Accepted |
| D-008 | Production keys, classical and PQC, live in an HSM or KMS | Accepted |
| D-009 | Signature domain separation (`QuantX-SIG-v1` payload) | Accepted |
| D-010 | `cryptography>=48,<51`, Python 3.11+ | Accepted |
| D-011 | Private factory, source slice per client | Accepted |
| D-012 | Configuration-driven composition | Accepted (schema is draft v1) |
| D-013 | Only the sidecar is containerized | Accepted |
| D-014 | Option availability gate | Accepted |
| D-015 | Small defaults (OTP, device link, Merkle, rate limiter, X25519 KEM) | Accepted |
| D-016 | The service terminates TLS itself | Accepted |
| D-017 | Regional profile warning; no FrodoKEM now | Accepted |

## Order of work

1. **Owner decisions:** done (D-007 to D-017). One item left: the `rotation_state` values and AAD field list for `vault_metadata.py`.
2. **Layers 0 and 1** (except files awaiting a decision).
3. **Golden vectors, then Layer 2**, written against the D-009 payload. Independent review gate.
4. **Layers 3 and 4, the first config schema and CLI, and the sidecar.** Recipe A runs from a file.
5. **Layers 5 to 10** as their decisions land.
6. **Conformance suites** per interface; Recipes A, B and C pass end to end in CI.
7. **The factory:** slicer, generator, builder export, release pipeline, slice-leak tests.
8. **Independent review, legal documents, pilot client build.**

## Still open

- The `rotation_state` values and AAD field list (`docs/INFERENCE_TRIAGE.md`).
- Golden vectors for signatures, KEM and the HKDF binding (S-002).
- Verify vendor claims in D-008 (AWS KMS, Google Cloud KMS, PKCS#11 PQC modules, SoftHSMv3 or kryoptic for CI) and that Vault PQC key support is not assumed (S-016).
- Prove the service can enforce and read the hybrid TLS group, or ship a terminator in the image (S-017).
- Lawyer review: licence, NDA, export controls, trademark (`docs/16`).
- An independent security reviewer and a review plan for the gated components.
- Re-verify upstream facts: pyca releases after 48 and SoftHSM2 PQC support (S-012).
- File-level specs for `factory/` (S-015) and an updated builder (S-013).

## First client delivery: definition of done

- The client config validates with no errors and its warnings are explained to the client.
- The slice reproduces byte for byte, passes its own tests and vectors, and passes the slice-leak test.
- Every `gated` component in it has a sign-off record, or the build is labelled `unreviewed` in the manifest.
- Licence, NDA and escrow terms are signed after legal review.
- The build manifest, SBOM, lockfile and signed sidecar image are delivered.
- The patch and support terms are agreed.

## Risks

- The factory is the product. If it leaks, the business model is exposed, so keep it private and small in access.
- PQC support in pyca and in HSM/KMS products is recent and partly unverified, so each backend claim needs checking before a client is promised it.
- Per-client builds multiply patch work unless rebuilds are automated.
- Production custody needs real hardware or cloud accounts for testing, and KEM keys on `aws_kms` are not possible today.
- Cryptographic export rules and licence terms vary by country, so get legal advice early.
