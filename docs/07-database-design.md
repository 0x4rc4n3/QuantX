# QuantX — Data Model

**Status:** Pre-implementation · **Depends on:** `06-system-architecture.md` Layer 0 (`KeyValueStore`, `ReplayStore`, `RateLimiter` interfaces)

## Why this isn't a relational schema

QuantX has no ORM and no SQL schema by design — all state goes through `KeyValueStore`. Every stateful component is backend-agnostic — the same logical entity can live in an in-memory dict (Recipe A) or a networked backend (Recipe B) without the component that owns it changing at all. This doc specifies the **logical key/value shape** each component relies on, which is the actual data-model contract in this architecture.

## Backend implementations (what actually stores the bytes)

| Backend | Used by | Note |
|---|---|---|
| `InMemoryKVStore` | Recipe A / dev / test | Hard `max_entries` cap (SR-3). Never a production recommendation. |
| Networked backend (e.g. Redis) | Recipe B / production | Explicit handling of network failure — fail-closed vs. degrade is a stated decision, not an unhandled exception (SR-4). |
| `EncryptedFileBackend` (key custody only) | Recipe A/B key storage | AES-GCM, vault metadata included in AAD (SR-9). |
| `OSKeychainBackend` / `HsmPkcs11Backend` | Recipe B key storage | Real integration (`HsmPkcs11Backend` built against SoftHSM2 as its dev target) or explicit `NotImplementedError`/`BackendUnavailableError` — never a silent in-memory fallback (SR-6). |

## Logical entities

### Challenge (Layer 4)

| Field | Notes |
|---|---|
| `challenge_id` | Key |
| `subject_id` | Who it was issued to |
| `nonce` | Random bytes, canonicalized via `JCSCanonicalizer` before signing |
| `issued_at` | From injected `Clock`, never wall-clock read directly (SR-14) |
| `expires_at` | TTL-backed |
| `required_mode` | Set server-side at issuance; never trusted from a later client message (SR-1) |

TTL: short-lived, expires unconsumed challenges automatically at the backend level where supported, or via explicit expiry check (in-memory).

### Session token (Layer 4)

| Field | Notes |
|---|---|
| `token_id` | Key |
| `subject_id` | |
| `issued_at` / `expires_at` | Via `Clock` |
| `factors_completed` | Set only once every required gate (incl. Layer 5 second factor, if configured) has passed — never partially populated with a live token attached (SR-10) |

### Replay record (`ReplayStore`, cross-cutting)

| Field | Notes |
|---|---|
| `token` (challenge ID, session token, backup code, or push-approval ID) | Key |
| `consumed_at` | Written atomically with the consume operation — `consume_once` semantics, not check-then-write |

Applies uniformly to: challenge responses, session tokens, backup codes, and push-approval tokens (SR-11). TOTP's one-time nature is inherent to the algorithm, not `ReplayStore`-tracked.

### Rate-limit counter (`RateLimiter`, cross-cutting)

| Field | Notes |
|---|---|
| `identity_key` (e.g. `subject_id` or `global`) | Key |
| `window_start`, `count` | Sliding/fixed window per implementation |

Two independent instances are wired in practice: per-identity and global (FR-4.4), plus a separate one for TOTP (FR-5.2) and for push-issuance (SR-5).

### TOTP/HOTP secret (Layer 5)

| Field | Notes |
|---|---|
| `subject_id` | Key |
| `secret` | Stored exclusively via `KeyWallet` (Layer 6), wired through as soon as it exists (D11) — no interim `KeyValueStore`-backed secret store |
| `counter` (HOTP only) | Incremented on each successful verify |

### Key custody vault entry (Layer 6–7)

| Field | Notes |
|---|---|
| `key_id` | Key |
| `encrypted_key_material` | Backend-specific |
| `vault_metadata` (algorithm, created_at, rotation_state) | Included in AEAD AAD, not stored alongside unauthenticated (SR-9) |

### Backup code record (Layer 6–7)

| Field | Notes |
|---|---|
| `subject_id` + `code_hash` | Key |
| `consumed` | Set via `ReplayStore`-style consume-once, never re-verifiable after use |

### Threshold policy / approval (Layer 8)

| Field | Notes |
|---|---|
| `policy_id` | Key |
| `required_keys` (set) | Duplicate-key rejection enforced at policy-creation time (SR-12) |
| `approvals` (list, per finalize attempt) | |

### CryptoBOM entry (Layer 10)

| Field | Notes |
|---|---|
| `finding_id` | Key |
| `source` (`static_scan` / `tls_inspect`) | |
| `trust` (`verified` / `unverified`) | Set explicitly for TLS findings (SR-13) |
| `algorithm`, `key_size`, `location` | |

## What's deliberately not modeled here

No `users` table, no `organizations` table, no `tenant_id` column anywhere. See `11-multi-tenancy-model.md` for why: isolation in this architecture happens at the deployment/composition level, not the row level.
