# QuantX Decision Log

This file records decisions that affect implementation but are not fully specified by the foundational documents. It is part of the builder handoff and must be updated when a new ambiguity is resolved.

## D-001 — Canonical package tree

**Status:** Accepted.

`docs/14-directory-structure.md` is authoritative for the repository tree. `quantx-core` is Layer 0, `quantx-crypto-adapters` is Layer 1, and `quantx-registry` is Layer 3. `docs/06-system-architecture.md` has been corrected to match this layout.

## D-002 — Specification-to-source conversion

**Status:** Accepted.

A file that describes a target implementation ends with `.md` only because it is a specification. The builder creates the target by removing the final `.md` suffix. Documentation files remain Markdown and are not converted. The complete mapping is defined in `BUILD_INSTRUCTIONS.md`.

## D-003 — Anonymous proof implementation

**Status:** Deferred by security rule.

`AnonymousProofBackend` remains an interface-only component. It must not receive an unaudited placeholder implementation. Implementation requires a specific vetted construction, a test plan, and independent qualified review.

## D-004 — HSM development target

**Status:** Accepted.

`HsmPkcs11Backend` is developed and tested against SoftHSM2 or another real PKCS#11 module. A fake backend may be used for isolated unit tests, but it does not satisfy integration coverage or production readiness. SoftHSM2 cannot hold ML-DSA/ML-KEM keys; see D-008 for how PQC key material is handled.

## D-005 — Replacement architecture contract

**Status:** Accepted for AI-builder implementation; independent security review still required.

The previously referenced `QuantX-v2-Architecture.md` was not available. `docs/QUANTX-V2-ARCHITECTURE.md` is the replacement versioned contract. It fixes the foundational interface signatures, mode identifiers, signature and KEM wire formats, bounds, parser failures, KEM HKDF parameters, session sequence, reference service boundary, and required golden vectors. It is normative for implementation but does not constitute security approval. Any future incompatible change must increment its version and update this decision.

## D-006 — PQC backend: pyca/cryptography replaces liboqs

**Status:** Accepted (project owner, 2026-10-03). Independent review of the PQC adapters is still required before any production claim; acceptance of the backend choice is not a security approval.

**Context.** `cryptography` (pyca) added ML-KEM and ML-DSA in 47 (AWS-LC/BoringSSL only) and in its OpenSSL-backed wheels from 48. Per the Trail of Bits post of 2026-06-30, v48 has no SLH-DSA and upstream work had only started; whether a later release adds it was not verified on 2026-10-03 and must be re-checked before unblocking. pyca private keys are seed-only (ML-KEM 64 B, ML-DSA 32 B), `encapsulate` returns `(shared_secret, ciphertext)`, and `verify` takes `(signature, data)`. ML-DSA `sign`/`verify` accept an optional context of up to 255 bytes.

**Resolution.**
1. PQC adapters (ML-DSA-65/87, ML-KEM-768/1024) wrap `cryptography>=48,<51` (D-010). `liboqs` is removed everywhere.
2. The `liboqs` research-grade disclosure is replaced by the PQC backend statement (`docs/10-security-requirements.md`): name the library, say its PQC support is recent, make no FIPS-validation claim unless the backend build is validated.
3. Adapters convert key and argument order to the Layer-0 contracts, store seed-form private keys (see D-007), and probe backend support at construction. `UnsupportedAlgorithm` is a loud typed error, never a failed verification.
4. SLH-DSA stays specified but blocked on upstream. No substitute library. `AlgorithmId.SLH_DSA` is reserved, no adapter or test is created, and the registry fails closed on any `AlgorithmId` with no adapter. This is an upstream-gated exception to D10/D12 (like `AnonymousProofBackend`'s audit gate), not a schedule deferral.

**Alternatives considered.** Keep `liboqs` for SLH-DSA only (rejected: keeps the dependency and its disclosure for one algorithm); drop SLH-DSA from the spec (rejected: loses the hedge against a lattice-specific break once pyca ships it).

**Affected.** D1, D10, FR-1.2, `docs/02`, `04`, `05`, `06`, `10`, `14`, `QUANTX-V2-ARCHITECTURE.md` §12, `BUILD_INSTRUCTIONS.md`, `quantx-crypto-adapters` (pqc specs, tests, pyproject, READMEs), `AlgorithmId`.

## D-007 — Software-custody key format (seed-only PQC keys)

**Status:** Accepted (project owner, 2026-10-04). Scope: software custody only (`memory_raw`, `encrypted_file`, `os_keychain`), meaning dev and staging. Production keys are HSM-resident (D-008) and no key bytes exist in application memory.

**Context.** `cryptography` exports ML-DSA and ML-KEM private keys only as seeds (`private_bytes_raw()`, `from_seed_bytes()`) and cannot import an expanded secret key.

**Resolution.** The vault stores the seed as `key_material` and an AAD-authenticated `key_format` tag in `VaultMetadata`. Accepted values: `ed25519-raw-v1`, `ecdsa-p256-pkcs8-v1`, `x25519-raw-v1`, `mldsa65-seed-v1`, `mldsa87-seed-v1`, `mlkem768-seed-v1`, `mlkem1024-seed-v1`. Retrieval with an unknown `key_format` raises. Backups carry the seed and the tag. Python gives only best-effort zeroization; no doc may claim otherwise. The `rotation_state` value set and the AAD field list remain unresolved and must be accepted before `vault_metadata.py` is implemented.

**Affected.** `vault_metadata.py`, `key_wallet.py`, `encrypted_file_backend.py`, `os_keychain_backend.py`, `backup_code_manager.py`, `docs/07-database-design.md`, `test_sr_09`.

## D-008 — Key residency: HSM or cloud KMS holds both classical and PQC private keys

**Status:** Accepted (project owner, 2026-10-04). Vendor capability statements below come from vendor and press sources that partly conflict; each must be verified against the vendor's own documentation before a client is promised it (S-016).

**Context.** Professional deployments keep private keys in an HSM or a managed KMS, never in application memory. `cryptography` signs and decapsulates in-process, so it cannot use a key that stays inside an HSM. SoftHSM2 2.7 has no ML-DSA/ML-KEM mechanisms.

**Resolution.**
1. In production profiles, every private key, classical and PQC, is generated and used inside an HSM or cloud KMS. `cryptography` performs verification and public-key operations only. Software custody is allowed in `dev` and `staging` only (E7).
2. Key custody backends: `hsm_pkcs11` (a module that reports PKCS#11 3.x PQC mechanisms), `aws_kms`, `gcp_kms`. Azure Key Vault and Managed HSM are not offered: no PQC key types as of August 2026 per the sources found.

   | Backend | Classical signing | ML-DSA signing | ML-KEM decapsulation |
   |---|---|---|---|
   | `hsm_pkcs11` | yes | yes, if the module advertises it (a validated HSM such as Luna T7 is reported to) | yes, same condition |
   | `aws_kms` | per key spec table | yes (ML-DSA-44/65/87, per AWS) | no ML-KEM key type |
   | `gcp_kms` | per key spec table | yes (ML-DSA, SLH-DSA, per Google) | preview only |
3. The Layer 0 `Signer` and `KEMProvider` interfaces do not change: a custody backend returns a `Signer` or decapsulator bound to a key handle. Wallet backends gain `generate`, `signer_for` and `decapsulator_for`; `retrieve` raises `KeyNotExportableError` for resident keys.
4. D-006 is amended: adapters wrap `cryptography` for verification, public-key operations and software custody; private operations on resident keys go through the custody backend. SLH-DSA stays blocked in `QuantX` even where a KMS offers it, until it can be used with a software verifier we ship.
5. Testing: SoftHSM2 covers classical keys and AES only. PQC on PKCS#11 needs SoftHSMv3 or kryoptic (availability to verify) or a vendor test HSM; KMS backends are tested against recorded or mocked clients plus a real-account smoke test. Software custody never counts toward a production claim.
6. The `custody.pqc_key_storage` field and the "wrapped seed" option are withdrawn.
7. HashiCorp Vault is supported as a source of secret references only (`vault:path` in `_ref` fields, for PINs, URLs and credentials). Vault is not a PQC key custody backend: Vault PQC key support was not verified.
8. Cloud credentials come from the platform identity (for example workload identity), never from the config file.

**Consequences.** Strongest security story for banks and regulated clients. Real hardware or cloud accounts are needed for CI, signing latency is a network or device round trip, and KEM keys on `aws_kms` are impossible today.

**Affected.** `hsm_pkcs11_backend.py`, new `aws_kms_backend.py` and `gcp_kms_backend.py`, `wallet_backend_interface.py`, `key_wallet.py`, `docs/15`, `docs/10` SR-6, `docs/adr/key_wallet_backends.md`.

## D-009 — Signature domain separation

**Status:** Accepted (project owner, 2026-10-04). Signature golden vectors (S-002) must now be written against it.

**Resolution.** Every component signature is computed over one uniform payload: `b"QuantX-SIG-v1\x00" || u8(mode) || u16(len(role_id)) || role_id || u32(len(message)) || message`, built from the canonicalized message (mirrors the KEM `info` construction in V2 §7). ML-DSA `context=None`. Cross-role and cross-mode replay vectors are required. Each custody backend's maximum message size is checked at startup; a payload over the limit fails closed.

**Why.** It protects the classical leg, which has no context parameter, and works unchanged for software and HSM or KMS signers.

**Affected.** V2 §8 and §11, `signature_combiner.py`, `signature_mode_enforcement.py`, ML-DSA adapters, `docs/04` FR-2, `test_sr_01`.

## D-010 — Dependency pin and platform policy

**Status:** Accepted (project owner, 2026-10-03).

**Resolution.**
1. Package metadata declares `cryptography>=48,<51`. The exact version comes from the lockfile (D6) that CI and service images install from. This reconciles `docs/06`'s "pinned exactly" rule with a publishable library: the lockfile is exact, the metadata range is bounded and reviewed.
2. Raising the upper bound requires reading the new release's changelog for PQC API changes and re-running the adapter and vector suites. pyca's PQC class names were changed during development (`MlDsa*` to `MLDSA*`, April 2026), which is why adapters probe support at construction.
3. Python 3.11+ for every package, per `QUANTX-V2-ARCHITECTURE.md` §2 (the earlier "3.9+" in the adapters' pyproject spec is withdrawn).
4. Wheels bundle OpenSSL 3.5 or later; source builds against older OpenSSL or LibreSSL lack ML-KEM/ML-DSA and fail the construction probe. From 49.0.0 there are no x86_64 macOS wheels.

**Affected.** every `pyproject.toml.md`, `docs/06`, `docs/10`, `BUILD_INSTRUCTIONS.md`.

## D-011 — Delivery model: private factory, generated source slice per client

**Status:** Accepted (project owner, 2026-10-04). Licence and contract terms need review by a lawyer before the first client delivery.

**Context.** The business model (D3) is per-client migration consulting and custom composed auth. The framework is the company's asset. Clients may read the code of the components they receive, because transparency matters in cryptography. The goal is to stop others from freely copying the business style or using the framework themselves.

**Resolution.**
1. The full framework and the tooling that composes it (the "factory", `docs/16-delivery-and-factory.md`) stay in a private repository and are never delivered.
2. A client receives a generated source slice for their own configuration: the packages and files that configuration needs, wiring frozen to their choices, a lockfile, an SBOM, the matching tests and vectors, and a build manifest.
3. Protection comes from licence terms, contracts, trade-secret handling of the factory, the QuantX trademark and per-client build identifiers. Obfuscation and compiled wheels are not relied on.
4. Delivery options: source slice (default), hosted sidecar run by the company (optional), source escrow (optional).
5. A build is labelled `unreviewed` unless a sign-off record from someone other than its author is in its manifest (P7, SR-6, SR-15).

**Alternatives considered.** Open-source the whole framework (rejected: gives competitors the factory). Ship compiled wheels only (rejected: weak protection, harder for clients to audit). Hosted platform for all clients (rejected for now: conflicts with D3 and `docs/11`).

**What this does not protect.** The idea and the business model are not protectable, and a competitor can reimplement a component after reading it. The edge is the factory, review quality, speed and maintenance.

**Affected.** `docs/11`, `docs/16`, `FINAL_PLAN.md`, `docs/02`, `docs/14`, `BUILD_INSTRUCTIONS.md`.

## D-012 — Configuration-driven composition

**Status:** Accepted as a principle (project owner, 2026-10-04). The field-level schema in `docs/15-config-and-composition.md` is draft v1 and becomes normative when Layer 4 and the sidecar are built.

**Resolution.**
1. One configuration file (`quantx.yaml`) selects every replaceable part. A new recipe or client configuration needs no code edit.
2. One rule table, one implementation of the checks, shared by the CLI, service startup, the factory builder and the slicer.
3. The loader fails closed: an unknown key, blocked option, unsupported mix, unreachable backend or missing secret reference stops startup with a typed error. It never falls back to a weaker part.
4. Secrets are never in the file. The file holds references (`env:`, `file:`) only.
5. Options in blocked or interface-only status are refused by the validator, never stubbed.
6. A thin CLI (`quantx init|validate|explain|run`) lives in the sidecar package.

**Alternatives considered.** Code-based wiring per client (rejected: every client becomes a fork). A free-form scripting config (rejected: config is data, not code).

**Affected.** `docs/15`, `service/config.py`, `service/wiring.py`, `service/cli.py`, `quantx-session/default_setup.py`, the factory builder.

## D-013 — Containers

**Status:** Accepted (project owner, 2026-10-04).

**Resolution.** Components are libraries, not containers. Container images are used for: the REST sidecar (one hardened image: non-root, read-only filesystem, no secrets baked in, base image pinned by digest, lockfile install), the dev/CI environment (OpenSSL 3.5 or later, SoftHSM2, Redis), and optionally a hosted-sidecar delivery (D-011). Images are signed, have an SBOM and are scanned in CI. A container is packaging and isolation, not a control for the cryptography itself.

**Alternatives considered.** One container per component (rejected: turns in-process calls carrying keys and shared secrets into network calls, adds failure modes inside the fail-closed path, and makes review harder).

**Affected.** `service/Dockerfile`, CI, `docs/06`.

## D-014 — Option availability gate

**Status:** Accepted (project owner, 2026-10-04).

**Resolution.** An option appears as `available` in the config schema and the builder only when (a) it passes the conformance suite for its Layer 0 interface and (b) every recipe that uses it passes its end-to-end test in CI. Options that are built but need independent review are `gated`. Options that cannot work yet are `blocked` (SLH-DSA) or `interface-only` (anonymous proofs) and are refused by the validator.

**Affected.** every interface under `quantx-core/interfaces`, `tests/`, `docs/15`, the factory builder.

## D-015 — Small defaults

**Status:** Accepted (project owner, 2026-10-04).

**Resolution.**
- **TOTP:** RFC 6238, HMAC-SHA1, 6 digits, 30 s step, accept plus or minus one step. Each accepted step is consumed through `ReplayStore`.
- **HOTP:** counter stored in the wallet, look-ahead window 10, the counter advances only after a successful verification.
- **OTP implementation:** standard-library `hmac`, checked against the RFC 4226 and RFC 6238 test vectors. No third-party OTP dependency.
- **Lockout:** thresholds come from config and are enforced by an independent `RateLimiter` instance per factor.
- **Device-link token:** 256-bit random, single use through `ReplayStore`, 10-minute expiry from the injected `Clock`. Methods: `issue_pairing_token(subject_id) -> str`, `consume_pairing_token(token) -> bool`.
- **Merkle tree:** SHA-256, one-byte prefixes (`0x00` leaf, `0x01` node), an odd node is promoted without duplicating the last leaf. Vectors required.
- **Rate limiter:** fixed window counter through `KeyValueStore`; boundary behavior stated and tested.
- **X25519 as a KEM:** fresh ephemeral key pair per `encapsulate`, ciphertext is the 32-byte ephemeral public key, shared secret is the raw Diffie-Hellman output, an all-zero output is rejected. The combiner binds both sides in the HKDF input.

**Affected.** TOTP/HOTP providers, `device_linker.py`, `merkle_tree.py`, `in_memory_rate_limiter.py`, `x25519_adapter.py`, authenticator `pyproject`.

## D-016 — TLS termination: the service terminates TLS itself

**Status:** Accepted (project owner, 2026-10-04).

**Resolution.**
1. The QuantX service process terminates TLS and reads the negotiated group from the live connection. No proxy header is trusted, so there are no proxy-trust settings.
2. Deployments behind an external TLS-terminating proxy are unsupported. Configuration that names one is rejected at startup.
3. mTLS and bearer authentication are mutually exclusive: configuring both is an error (E6) and startup fails.
4. If the Python and OpenSSL stack in use cannot restrict and read the negotiated group, the image ships a TLS terminator we control in front of the app, inside the same image, passing the group over a local socket. Either way an end-to-end test must show that a client without the hybrid group is rejected. Whether the plain Python stack can do this is unverified (S-017).

**Consequence.** Strongest enforcement of the hybrid group (SR-13). Clients must provision certificates to the service.

**Affected.** `hybrid_tls_enforcement.py`, `config.py`, `mtls_auth.py`, `bearer_token_auth.py`, `service/Dockerfile`, `docs/15`.

## D-017 — Regional profile and FrodoKEM

**Status:** Accepted (project owner, 2026-10-04).

**Resolution.** `PQC_ONLY` mode prints a warning (W10) that France (ANSSI) and Germany (BSI) do not accept standalone PQC during the transition, so such a profile cannot serve those markets. FrodoKEM is not added now: pyca has no FrodoKEM, so adding it needs a new library and an amendment to D-006. Revisit if a French or German client requires it. Delivery stays source-slice first with hosted as an option (D-011).

**Affected.** `docs/15` (W10), the builder, `FINAL_PLAN.md`.

## Change protocol

Each new decision must include an identifier, status, context, selected resolution, alternatives considered when material, and the documents or tests affected. A decision that changes a security requirement requires review before implementation proceeds.
