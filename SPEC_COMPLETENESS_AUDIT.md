# QuantX Specification Completeness Audit

**Audit status:** Conditional handoff, revised 2026-10-04 for the delivery model and configuration-driven composition (D-011 to D-014). Layers 0 and 1 can start now with the stops listed below. Layer 2 and everything above it are gated on open decisions and golden vectors.

## Executive conclusion

The repository is **not certified contradiction-free and not every target `.md` file contains enough information to generate a perfect implementation without engineering judgment**. `docs/QUANTX-V2-ARCHITECTURE.md` fixes the central interface, wire-format and KEM-binding contract. The remaining gaps are narrower than in the previous revision and are now listed in `docs/INFERENCE_TRIAGE.md` and `docs/DECISIONS.md` instead of being spread across about 150 markers.

An AI builder may begin inventory, repository conversion, Layer 0 (except the rate limiter), classical and PQC adapter logic, test harness setup, and documentation cleanup. It must not silently finalize unresolved cryptographic APIs, wire formats, deployment topology, or security policy choices.

## Layer readiness

| Layer | State | What is still needed |
|---|---|---|
| 0 Core | Ready | Nothing blocks it: the rate limiter is a fixed window (D-015). |
| 1 Adapters | Ready | X25519 KEM mapping decided (D-015). Verification and public-key work use pyca; private operations on resident keys go through custody backends (D-008). SLH-DSA stays blocked (D-006). |
| 2 Combiners | Needs vectors | Signed payload decided (D-009). Write the golden vectors, then independent review gate. |
| 3 Registry | After Layer 2 | Signed-config scheme follows the Layer 2 decisions. |
| 4 Session | After Layers 0-3 | Concrete fixtures (S-005). |
| 5 TOTP/HOTP/push | After Layer 4 | OTP library and parameters (triage). |
| 6-7 Custody, recovery | Ready to specify and build | Key residency decided (D-008); new `aws_kms` and `gcp_kms` backend specs added. Needs verified vendor claims (S-016), PQC-capable PKCS#11 for CI, and the `rotation_state` value set. |
| 8 Threshold | After Layer 2 | None beyond review gate. |
| 9 Membership proofs | After Layer 4 | Merkle hash and domain separation (triage). `AnonymousProofBackend` stays interface-only. |
| 10 Compliance | Independent | Report format (accept). |
| Service | After Layer 4 | TLS is terminated by the service (D-016); proxy trust removed. Verify the Python TLS group check (S-017). Config schema is specified (`docs/15`, draft v1). |
| 11 Config and CLI | With Layer 4 | Accept schema v1 (S-013). Recipes A, B, C end to end. |
| 12 Factory (private) | After 11 and the layers it slices | Conformance suites, file-level factory specs (S-015), legal review (S-014). |

## Findings

| ID | Severity | Finding | Affected area | Required disposition |
|---|---|---|---|---|
| S-001 | Resolved | The previously referenced `QuantX-v2-Architecture.md` was unavailable. | `docs/QUANTX-V2-ARCHITECTURE.md` | Replacement contract recorded as D-005; future revisions require versioning and review. |
| S-002 | High | Signature and KEM wire formats are normative, but only three smoke vectors exist. In draft.1 two of them did not parse under the format they illustrate (a stray byte); fixed in draft.2 and the HKDF vector was independently recomputed and matches. Real-key vectors, malformed-input vectors and interoperability tests are still missing. | Wire-format modules, fuzz tests, `QUANTX-V2-ARCHITECTURE.md` §11 | Write the full vector set against the accepted D-009 payload. Parse every container vector with the real parser. |
| S-003 | Medium (was Critical) | KEM binding (HKDF-SHA256, `info` construction, IKM order), the hybrid AND rule and the signed payload (D-009) are now normative and decided. Remaining: write the vectors and pass independent review. | Combiner and adapter specs | Vectors, then review. |
| S-004 | Medium (was High) | Deployment model decided: the service terminates TLS and mTLS and bearer are exclusive (D-016). Still needed: end-to-end tests, including a client without the hybrid group being rejected. | Service middleware, auth, config | Verify the Python/OpenSSL stack can restrict and read the negotiated group, or ship a terminator in the image (S-017). |
| S-005 | High | Test and fixture specs say details are not specified. 24 marker lines need golden vectors for expected values, 48 can be written by the builder from the source spec. | Root and service test fixtures, end-to-end security tests | See `docs/INFERENCE_TRIAGE.md`. |
| S-006 | Low (was High) | 132 keyword-matched marker lines remain. Triage: 2 already decided, 1 line in 1 file must be decided (`rotation_state` and the AAD field list), 52 are acceptable inferences, 72 are test-fixture lines (24 need golden vectors), 5 are not markers or are open by design. | Multiple packages | Use `docs/INFERENCE_TRIAGE.md`. |
| S-007 | Medium | Pin and Python floor are now fixed (D-010). Still open: operational limits, timeout values, key sizes for the remaining algorithms, performance/SLO targets (D8), supported-OS matrix beyond the wheel note. | Package metadata, deployment, NFRs | Pin and document before release engineering. |
| S-008 | Medium | No generated API schema, compatibility policy, migration policy, or golden-vector bundle. | Public packages and service | Add before multiple downstream projects depend on the foundation. |
| S-009 | Resolved | D-006 (pyca replaces liboqs) was marked Proposed while the build instructions already relied on it. Now Accepted by the project owner; the "pending review" notes are removed. | D-006, handoff, security requirements, index | Done. Independent review of the adapters is still required before any production claim. |
| S-010 | Resolved | pyca seed-only keys, the HSM's PQC limits and signature domain separation are decided: D-007 (software custody format), D-008 (key-resident custody), D-009 (signed payload). Consequences are carried into the wallet, backend and combiner specs. | Wallet, HSM backend, combiners | Done. Independent review and vectors still required. |
| S-011 | Medium | Contradictions found and fixed in this revision: "pinned exactly, no `>=`" (docs/06) vs `cryptography>=48`; Python 3.9+ (adapters pyproject) vs 3.11+ (V2 §2); build-instruction sections numbered 10 before 9; `00-index.md` doc table omitting doc 14 and an empty change log. | Docs and pyproject specs | Resolved. Run a doc-vs-doc consistency check again after each decision. |
| S-012 | Medium | Some upstream facts were checked only partly. Confirmed from pyca sources: ML-KEM/ML-DSA in 48, seed-only keys, ML-DSA context up to 255 bytes, no SLH-DSA in 48. Not verified: any pyca release after 48 adding SLH-DSA, the "50.0.2" version claim (the 50.0.1 docs were seen), and the SoftHSM2 PQC statements (taken from third-party project notes). | D-006, D-008, SLH-DSA spec | Re-verify against pyca and SoftHSM release notes when implementing. |
| S-013 | Medium | Configuration schema is draft v1. The builder files in `factory/builder/` predate D-008, D-016 and D-017: they still offer only `hsm_pkcs11`, `os_keychain` and `encrypted_file` as custody, still export `pqc_key_storage: wrapped_seed`, and lack `aws_kms`, `gcp_kms`, W10 and W11. They must not be used to produce client configs until updated. | `docs/15`, `factory/builder/` | Update the builder to the doc 15 rule table and export format. |
| S-014 | High | Licence, NDA, escrow, export-control and trademark terms are listed as a checklist only (`docs/16`). Nothing is drafted or reviewed. No client delivery can happen before a lawyer has reviewed them. | `docs/16`, D-011 | Engage a lawyer with IP and software experience; review the checklist and draft the documents. |
| S-015 | Medium | `factory/` has a contract (`docs/16`) but no file-level specs, and no conformance suite specs exist per Layer 0 interface (D-014). | `factory/`, `quantx-core/tests` | Write the specs when build step 12 starts; do not call any option `available` before then. |
| S-016 | High | Vendor capability claims in D-008 come from vendor and press sources that partly conflict (older posts say no PQC key types). Verified only at the level of the AWS page and the August 2026 comparisons found. Vault PQC key support was not verified. | D-008, custody backends | Verify each claim in the vendor's own documentation and test with a real account before promising it to a client. |
| S-017 | Medium | Whether the plain Python and OpenSSL stack can restrict TLS groups and read the negotiated group is unverified. | D-016, service | Prove it with an end-to-end test, or ship a terminator we control inside the image. |

## What has been verified

The archive is structurally valid. The canonical package tree is consistent between `docs/06-system-architecture.md` and `docs/14-directory-structure.md`. The two container smoke vectors in V2 §11 now parse under §5 and §6, and the HKDF vector was recomputed with `cryptography` and matches. No `liboqs` dependency remains; the surviving mentions are "replaced by" notes. The scaffold still contains package, test, security, service and tool specifications that vary in precision. Nothing in this archive has been run: it contains no code and no test results.

## Hard-stop rule

The builder must stop and request a recorded decision before implementing any target file listed as MUST-DECIDE in `docs/INFERENCE_TRIAGE.md`, and any item still listed as open in this audit. It may implement mechanical scaffolding, ACCEPT items and non-behavioral documentation while those decisions are pending.

## Minimum gate before calling the specification complete

The project owner must provide or approve all of the following:

1. A normative API contract for every remaining public class and function.
2. Golden vectors and interoperability tests for the signature and KEM wire formats, the signed-message prefix (D-009) and the HKDF binding.
3. Accepted entries for each MUST-DECIDE row in `docs/INFERENCE_TRIAGE.md` (D-007 to D-017 are accepted).
4. A reference service deployment model, including TLS termination, authentication composition, configuration schema, error mapping, and observability behavior.
5. Concrete fixtures and expected outcomes for every unit, security, integration, and end-to-end test.
6. A supported-platform policy beyond D-010.
7. Independent security review plans and sign-off records for every gated component.
8. Lawyer-reviewed licence, NDA, escrow and export-control terms before any client delivery (S-014).
9. Conformance suites per interface and end-to-end tests for Recipes A, B and C (D-014).

## Decision

Until the minimum gate is satisfied, the correct label is **implementation scaffold / conditional AI-builder handoff**, not **complete foundation**, **perfect specification**, **secure library**, or **production-ready system**.

## References

[1]: BUILD_INSTRUCTIONS.md "QuantX AI-builder implementation contract"
[2]: AI_BUILDER_HANDOFF.md "QuantX AI-builder handoff"
[3]: docs/DECISIONS.md "QuantX decision log"
[4]: docs/INFERENCE_TRIAGE.md "QuantX inference triage"
[7]: docs/15-config-and-composition.md and docs/16-delivery-and-factory.md "Configuration and delivery"
[8]: FINAL_PLAN.md "QuantX final plan"
[5]: docs/10-security-requirements.md "QuantX security requirements"
[6]: docs/14-directory-structure.md "QuantX canonical directory structure"
