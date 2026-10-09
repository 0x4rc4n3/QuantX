# QuantX: Configuration and Composition

**Status:** Principles accepted (D-012). Field-level schema is draft v1 and becomes normative when Layer 4 and the sidecar are built. **Depends on:** `06-system-architecture.md`, `10-security-requirements.md`, `DECISIONS.md` (D-006 to D-010, D-012, D-014).

## Purpose

A QuantX backend is chosen, not coded. One file, `quantx.yaml`, picks the part for every replaceable slot. The same file drives the CLI, the sidecar at startup, the factory builder and the slicer (`16-delivery-and-factory.md`). Recipes A, B and C are three example files, not three code paths.

## Principles

| ID | Rule |
|---|---|
| CFG-1 | One file selects every replaceable part. Changing a recipe or a client setup needs no code edit. |
| CFG-2 | One rule table, one implementation. The CLI, service startup, builder and slicer call the same validator. |
| CFG-3 | Fail closed. Unknown key, blocked option, unsupported mix, unreachable backend, missing secret reference or bad signature stops startup with a typed error. Never fall back to a weaker part. |
| CFG-4 | No secrets in the file. Secrets are references (`env:NAME`, `file:/path`, `vault:path`) in keys ending in `_ref`. A literal value under any other secret-like key is an error. |
| CFG-5 | `quantx explain` prints the resolved wiring and warnings. It never prints secret values. |
| CFG-6 | Honest status. Blocked and interface-only options are refused, never stubbed. |
| CFG-7 | Config is data, not code: no expressions, no includes, no interpolation outside `_ref` values. |
| CFG-8 | The SHA-256 of the canonical config is logged at startup and recorded in the build manifest. |

## Slots and options

Status values: `available` (passes D-014), `gated` (built, independent review required), `blocked` (refused), `interface-only` (refused).

| Slot | Key | Options (status) |
|---|---|---|
| Mode | `mode` | `HYBRID` (available, default), `PQC_ONLY` (available, explicit opt-in), `CLASSICAL_ONLY` (available, explicit opt-in, warns) |
| Classical signature | `algorithms.signature.classical` | `ed25519`, `ecdsa-p256` (unused when mode is `PQC_ONLY`) |
| PQC signature | `algorithms.signature.pqc` | `ml-dsa-65`, `ml-dsa-87`, `slh-dsa` (blocked, D-006) (unused when mode is `CLASSICAL_ONLY`) |
| Classical KEM | `algorithms.kem.classical` | `x25519` (only option) |
| PQC KEM | `algorithms.kem.pqc` | `ml-kem-768`, `ml-kem-1024` |
| Registry | `registry.config_signing` | `unsigned` (dev only), `signed` (gated) |
| State store | `state.backend` | `memory`, `redis` |
| Key custody | `custody.backend` | `memory_raw` (dev only), `encrypted_file` (gated, dev/staging only), `os_keychain` (gated, dev/staging only), `hsm_pkcs11` (gated), `aws_kms` (gated), `gcp_kms` (gated) |
| Second factor | `second_factor` (list) | `totp`, `hotp`, `push` |
| Threshold | `threshold.enabled` | `false`, `true` (gated) |
| Membership proof | `membership_proof.backend` | `none`, `merkle` (gated), `anonymous` (interface-only) |
| Compliance | `compliance.scanners` (list) | `source`, `tls_inspector` |
| Service auth | `service.auth` | `bearer`, `mtls` (mutually exclusive, proposed default) |
| Transport check | `service.tls_enforcement` | `required`, `off` |
| Environment | `environment` | `dev`, `staging`, `production` |

Fixed parts with no alternative today: JCS canonicalizer, system clock, in-memory replay store, in-memory rate limiter, HKDF-SHA256 KEM binding.

## Validation rules

Errors stop startup. Warnings print in `validate` and `explain`.

| ID | Level | Rule |
|---|---|---|
| E1 | error | Unknown key, wrong type or unsupported `schema_version`. |
| E2 | error | A `blocked` or `interface-only` option is selected. |
| E3 | error | Algorithms do not match the mode: `HYBRID` needs one classical and one PQC for both signature and KEM; `PQC_ONLY` forbids classical entries; `CLASSICAL_ONLY` forbids PQC entries. |
| E4 | error | A secret-like key holds a literal instead of a `_ref`. |
| E5 | error | A required `_ref` is missing (for example `url_ref` with `redis`, `pin_ref` with `hsm_pkcs11`, `signing_key_ref` with `signed`). |
| E6 | error | `service.auth` names more than one method. |
| E7 | error | `environment: production` with `state.backend: memory`, `registry.config_signing: unsigned`, `tls_enforcement: off`, or software custody (`memory_raw`, `encrypted_file`, `os_keychain`). Production keys are HSM or KMS resident (D-008). |
| E8 | error | The custody backend cannot hold a configured algorithm per the capability table in D-008 (for example `aws_kms` with an ML-KEM algorithm). |
| W1 | warn | Mode is `CLASSICAL_ONLY`: no protection against harvest-now-decrypt-later (D2). |
| W2 | warn | Mode is `PQC_ONLY`: no hybrid safety net, pyca PQC support is recent (D-006). |
| W3 | warn | Signature and KEM are at different security levels. |
| W4 | warn | In-memory state with real custody or a signed registry: lost on restart, not shared between instances. |
| W5 | warn | Unsigned registry with `hsm_pkcs11` or `os_keychain`. |
| W6 | warn | Software custody: private keys sit in application memory (dev and staging only, D-007). |
| W7 | warn | No second factor (D4). |
| W8 | warn | Any `gated` option selected: needs independent review before a production claim. |
| W9 | warn | `tls_enforcement: off` outside production (SR-13). |
| W10 | warn | Mode is `PQC_ONLY`: France (ANSSI) and Germany (BSI) do not accept standalone PQC during the transition (D-017). |
| W11 | warn | `gcp_kms` with an ML-KEM algorithm: reported as preview only (D-008). |

The builder at `factory/builder/quantx-builder.html` shows the same checks. Its custody options and rules E7, E8, W6, W10 and W11 must be brought in line with this table, and the builder must export this file format (S-013).

## Schema (draft v1)

```yaml
schema_version: 1
environment: dev            # dev | staging | production
mode: HYBRID                # HYBRID | PQC_ONLY | CLASSICAL_ONLY
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry:
  config_signing: unsigned  # unsigned | signed
  signing_key_ref: null     # required when signed, e.g. file:/etc/quantx/registry.pub
state:
  backend: memory           # memory | redis
  url_ref: null             # required for redis, e.g. env:QUANTX_REDIS_URL
custody:
  backend: memory_raw       # memory_raw | encrypted_file | os_keychain | hsm_pkcs11 | aws_kms | gcp_kms
  key_id_ref: null          # aws_kms / gcp_kms: reference to the key (platform identity supplies credentials)
  module_ref: null          # hsm_pkcs11: env:QUANTX_PKCS11_MODULE
  slot_ref: null
  pin_ref: null
second_factor: [totp]       # totp | hotp | push
threshold: {enabled: false}
membership_proof: {backend: none}   # none | merkle
compliance: {scanners: []}          # source | tls_inspector
service:
  auth: bearer              # bearer | mtls
  tls_enforcement: off      # required | off
```

## Recipe examples

Recipe A (demo, one process):

```yaml
schema_version: 1
environment: dev
mode: HYBRID
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry: {config_signing: unsigned}
state: {backend: memory}
custody: {backend: memory_raw}
second_factor: [totp]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: []}
service: {auth: bearer, tls_enforcement: off}
```

Recipe B (enterprise, hybrid):

```yaml
schema_version: 1
environment: production
mode: HYBRID
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry: {config_signing: signed, signing_key_ref: "file:/etc/quantx/registry.pub"}
state: {backend: redis, url_ref: "env:QUANTX_REDIS_URL"}
custody:
  backend: hsm_pkcs11
  module_ref: "env:QUANTX_PKCS11_MODULE"
  slot_ref: "env:QUANTX_PKCS11_SLOT"
  pin_ref: "env:QUANTX_PKCS11_PIN"
second_factor: [totp, push]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: [source, tls_inspector]}
service: {auth: mtls, tls_enforcement: required}
```

Recipe C (PQC only):

```yaml
schema_version: 1
environment: production
mode: PQC_ONLY
algorithms:
  signature: {pqc: ml-dsa-87}
  kem:       {pqc: ml-kem-1024}
registry: {config_signing: signed, signing_key_ref: "file:/etc/quantx/registry.pub"}
state: {backend: redis, url_ref: "env:QUANTX_REDIS_URL"}
custody:
  backend: hsm_pkcs11
  module_ref: "env:QUANTX_PKCS11_MODULE"
  slot_ref: "env:QUANTX_PKCS11_SLOT"
  pin_ref: "env:QUANTX_PKCS11_PIN"
second_factor: [totp]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: [source]}
service: {auth: mtls, tls_enforcement: required}
```

## CLI contract (`quantx_service/cli.py`)

| Command | Behavior | Exit codes |
|---|---|---|
| `quantx init --recipe A\|B\|C` | Writes a starting `quantx.yaml`. Refuses to overwrite an existing file. | 0 ok, 2 invalid input |
| `quantx validate [--file F] [--env E]` | Runs E1 to E8 and W1 to W11. Prints results. Does not contact any backend. | 0 ok, 2 errors found |
| `quantx explain [--file F]` | Prints resolved wiring: which class fills each slot, status of each option, warnings, config hash. No secret values. | 0 ok, 2 errors found |
| `quantx run [--file F]` | Validates, then probes each backend (PQC support, Redis, PKCS#11), then starts the sidecar. | 0 clean stop, 2 invalid, 3 backend unavailable |

## Startup behavior (fail closed)

| Condition | Result |
|---|---|
| Redis unreachable | `BackendUnavailableError`, exit 3. No fallback to memory. |
| PKCS#11 module missing or PIN wrong | `BackendUnavailableError`, exit 3. |
| Backend lacks ML-DSA or ML-KEM (construction probe) | exit 3. Never reported as a failed verification. |
| Registry config signature invalid | exit 2. |
| Secret reference does not resolve | exit 2. |
| TLS is not terminated by this process, or both auth methods are set | exit 2 (D-016). |
| Custody backend reports no support for a configured algorithm, or a signing payload exceeds its message-size limit | exit 3. |

## Where it lives

No new package (D-001 tree stays). Schema, loader and validator go in the existing `quantx_service/config.py` and `quantx_session/default_setup.py`; wiring stays in `wiring.py`; the thin CLI is `quantx_service/cli.py`. If these grow, a dedicated `quantx-config` package is the next step and needs its own decision entry.

## Option availability

An option can be `available` only when it passes the conformance suite for its Layer 0 interface and every recipe that uses it passes its end-to-end test in CI (D-014). Until then it is `gated` or not offered.
