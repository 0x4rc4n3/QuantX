# QuantX v2 — Atomic, Crypto-Agile Architecture

**Status:** Design blueprint incorporating every fix from the QuantX Security Audit (C1, C2, H1–H4, M1–M7, L1–L2).
**Purpose:** a precise enough specification that the whole platform can be rebuilt from this document alone — every piece is atomic (one job each), depends only on shared interfaces (never on a sibling's concrete class), and can be re-arranged like Lego bricks into different deployments without touching its internals.

## How to read this document
Each component gets an identical spec block:

| Field | Meaning |
|---|---|
| **Layer** | Which architectural layer it lives in (0 = foundation, 10 = top) |
| **Depends on** | Interfaces (never concrete classes) it needs injected |
| **Implements** | Interface(s) it satisfies, so other pieces can consume it interchangeably |
| **Outside (Public Interface)** | Everything another component is allowed to call — this is the plug |
| **Inside (Internal Design)** | How it does its job — never relied upon by callers |
| **Wire format** | Exact bytes/JSON it produces or consumes, if any |
| **Security notes** | What it guarantees and what it explicitly does NOT guarantee |
| **Fixes** | Which audit finding this design resolves, if any |

Rule of thumb for "atomic": if you can't describe a component's job in one sentence without the word "and", split it.

---

## 1. Design Principles

1. **Dependency inversion, always.** Every component's constructor takes *interfaces* (Python `Protocol`/ABC types from Layer 0), never concrete sibling classes. A component that needs "something that signs" declares `Signer`, not `Ed25519Adapter`. This is what makes re-arrangement possible — swap any implementation of an interface without touching a single consumer.
2. **One algorithm per adapter, forever.** No component may contain an `if family == "pqc"` branch. Each cryptographic primitive (Ed25519, ML-DSA-65, X25519, ML-KEM-768, SLH-DSA...) gets its own tiny adapter file implementing a shared interface. Adding a new algorithm in the future = adding one new adapter, zero changes anywhere else. (This directly replaces the old monolithic `crypto-core/provider.py`, whose per-family dispatch logic was the root of several audit findings.)
3. **Combiners are generic, never pair-specific.** There is exactly one `SignatureCombiner` class and exactly one `KEMCombiner` class in the whole system. "Ed25519+ML-DSA-65" is not a component — it's just two adapter instances handed to the one generic combiner at configuration time. This is what "new+old algorithm pair" means architecturally: the *old* piece and the *new* piece are separate, swappable atoms; the pairing is runtime wiring, not code.
4. **Mode is a server-side configuration fact, never a client-supplied claim.** (Fixes **C1**.) The old bug was trusting a `mode` field inside the signature bytes. In v2, every verifier is constructed with its own `required_mode` and structurally cannot accept anything else — the wire format's self-declared mode is used only to know how to *parse* the bytes, and is cross-checked against `required_mode` before any cryptographic work happens. Mismatch = reject, unconditionally, before any signature math runs.
5. **No component invents its own persistence.** Anything that needs to remember state across calls (sessions, replay records, rate-limit counters, key material) depends on a `KeyValueStore`-shaped interface from Layer 0. The reference implementation is in-memory (for demos/tests); a production deployment swaps in a Redis- or DB-backed implementation of the *same interface* with zero changes to the component using it. (Fixes **H1**, **H2**.)
6. **Every claim in a docstring must be true today, not aspirationally.** A component that doesn't yet do hardware-backed storage says so and raises `NotImplementedError`, rather than quietly behaving like a dict while claiming otherwise. (Fixes **H4**.)
7. **Canonicalization is one shared component, used by everyone who signs structured data.** No module hand-rolls `json.dumps(..., sort_keys=True)` for anything that gets cryptographically signed. (Fixes **M2**.)
8. **Anything that claims "zero-knowledge" must be independently reviewable as such, or must not use that word.** The Merkle-membership component in v2 is explicitly, honestly labeled as a *sound but non-anonymous* membership proof (it verifies real membership; it does not hide the member's position). Actual anonymity is isolated behind a pluggable, mandatory-audit-gated interface so a real, vetted ZK backend can be dropped in later without touching any caller. (Fixes **C2**.)

---

## 2. The Component Contract

Every atomic component, regardless of layer, is a single package with:
- One public class or function set — its "Outside."
- Zero imports of another Layer-N-or-above component's concrete class. Only Layer 0 interfaces may be imported directly.
- A `GATE_REVIEW_REQUIRED: bool` class attribute if the component touches novel cryptographic composition (hybrid combiners, threshold auth, anonymous proofs) — `True` means "do not deploy to production before independent cryptographic review," matching the discipline the original codebase already used well.
- No global/module-level singletons that hold mutable state. (The old codebase's `_DEFAULT_PROVIDER` / `_DEFAULT_REGISTRY` singletons made testing and multi-tenant use awkward — v2 requires explicit construction and injection everywhere.)


---

## 3. Layer 0 — Foundational Interfaces

These are the only types any component is allowed to depend on directly. None of them contain logic — they're contracts.

### 3.1 `Signer` / `Verifier`
**Layer:** 0 · **Implements:** nothing (base contract) · **Depends on:** nothing

**Outside:**
```
class Signer(Protocol):
    algorithm_id: str            # e.g. "Ed25519", "ML-DSA-65"
    family: Literal["classical", "pqc"]
    def generate_keypair() -> KeyPair
    def sign(message: bytes, private_key: bytes) -> bytes

class Verifier(Protocol):
    algorithm_id: str
    family: Literal["classical", "pqc"]
    def verify(message: bytes, signature: bytes, public_key: bytes) -> bool   # never raises; False on any malformed input
```
**Security notes:** `verify()` must fail closed — any exception inside an adapter's own `verify()` is caught internally and converted to `False`. Callers may assume `verify()` is total (never throws) and constant-time-safe on the comparison itself (the underlying library's job, not the adapter's).

### 3.2 `Encapsulator` / `Decapsulator`
**Layer:** 0

**Outside:**
```
class KEMProvider(Protocol):
    algorithm_id: str             # e.g. "X25519", "ML-KEM-768"
    family: Literal["classical", "pqc"]
    def generate_keypair() -> KeyPair
    def encapsulate(public_key: bytes) -> tuple[ciphertext: bytes, shared_secret: bytes]
    def decapsulate(ciphertext: bytes, private_key: bytes) -> bytes   # shared_secret
```

### 3.3 `Canonicalizer`
**Layer:** 0 · **Fixes M2**

**Outside:**
```
class Canonicalizer(Protocol):
    def canonicalize(value: dict | list | str | int | float | bool | None) -> bytes
```
**Reference implementation — `JCSCanonicalizer` (Layer 1, atomic):** implements RFC 8785 (JSON Canonicalization Scheme) exactly — fixed number formatting (no trailing zeros, no exponent form for integers), lexicographic key ordering by UTF-16 code unit (not Python's default string sort), and mandatory UTF-8 output. Every other component in the system that needs to sign or hash structured data (`Challenge`, `DecisionProposal`, `ZKPProof` statements, audit-log entries) takes a `Canonicalizer` in its constructor and calls it — none of them format JSON themselves. This is the single reusable fix for every canonicalization bug: implement RFC 8785 once, correctly, and inject it everywhere.
**Security notes:** RFC 8785 is chosen specifically because it's a formal, language-independent spec — a Go, Rust, or Java client implementing JCS produces byte-identical output to this Python component for the same logical document, which the old `json.dumps(sort_keys=True)` approach could not guarantee.

### 3.4 `Clock`
**Layer:** 0

**Outside:** `class Clock(Protocol): def now() -> float`
**Why this exists at all:** every time-based component (challenges, TOTP, rate limiter, session TTLs) takes a `Clock` instead of calling `time.time()` directly. This makes every time-based security property in the system independently unit-testable without monkeypatching, and is a prerequisite for the "no component invents its own persistence/state" rule — a `Clock` is itself swappable state.

### 3.5 `KeyValueStore`
**Layer:** 0 · **Fixes H1, H2**

**Outside:**
```
class KeyValueStore(Protocol):
    def get(key: str) -> bytes | None
    def set(key: str, value: bytes, ttl_seconds: float | None) -> None
    def delete(key: str) -> None
    def set_if_not_exists(key: str, value: bytes, ttl_seconds: float | None) -> bool   # atomic compare-and-set primitive
```
**Reference implementations (both Layer 1, atomic, both implement this one interface):**
- `InMemoryKVStore` — a single dict with a background reaper thread that evicts by TTL and enforces a hard `max_entries` cap (default configurable; once hit, oldest-TTL entries are evicted first, and new inserts beyond the cap are rejected rather than growing unbounded). This alone closes the unauthenticated memory-exhaustion DoS from the audit (H1) — there is no path to unbounded growth because the cap is enforced at the one shared primitive every stateful component uses.
- `RedisKVStore` — thin wrapper over `SETEX`/`SET NX EX`/`GET`/`DEL`. Because it satisfies the exact same interface, every component built against `KeyValueStore` (sessions, replay store, rate limiter, TOTP used-step tracking, push challenges) becomes horizontally scalable across multiple app instances by changing one line of wiring code (H2) — no component code changes.
**Security notes:** `set_if_not_exists` is the *only* primitive replay protection and rate limiting are allowed to use for their core check-then-write step, specifically so the atomicity guarantee (fixing the class of race condition the audit checked for and didn't find, but which is easy to introduce by accident in future changes) lives in one place instead of being re-implemented per component.

### 3.6 `ReplayStore`
**Layer:** 0 — thin, purpose-named wrapper over `KeyValueStore`

**Outside:**
```
class ReplayStore(Protocol):
    def consume_once(token_id: str, ttl_seconds: float) -> bool   # True = first use (proceed), False = already used (reject)
```
**Inside (reference impl):** `consume_once` = one call to the injected `KeyValueStore.set_if_not_exists`. That's the entire component — intentionally trivial, because the hard part (atomicity) is already solved once in Layer 0.

### 3.7 `RateLimiter`
**Layer:** 0

**Outside:**
```
class RateLimiter(Protocol):
    def check_and_record(key: str, limit: int, window_seconds: float) -> bool   # True = allowed, False = limited
```
**Reference implementation:** sliding-window counter stored as a single `KeyValueStore` entry per key (a small serialized list of timestamps, capped at `limit` entries — so per-key memory is bounded by `limit`, and total memory is bounded by the `KeyValueStore`'s own `max_entries` cap). A **global** limiter instance (fixed key, e.g. `"__global__"`) is composed alongside every per-identity limiter at the orchestration layer (Layer 4) specifically to close the "rotate the key to dodge the limit" gap from the audit (H1) — per-key limits stop credential stuffing against one identity; the global limit stops volumetric abuse regardless of how many identities an attacker manufactures.

### 3.8 Shared Types
**Layer:** 0 — pure data, no logic, no dependencies

These types are referenced throughout the architecture. Every one is an immutable value object (frozen dataclass or `NamedTuple`) — none contain behavior.

```python
from enum import Enum
from typing import NamedTuple

class Mode(Enum):
    HYBRID = "HYBRID"                # Both classical + PQC required (default, D2)
    CLASSICAL_ONLY = "CLASSICAL_ONLY" # Explicit opt-in: classical component only
    PQC_ONLY = "PQC_ONLY"             # Explicit opt-in: PQC component only

class KeyPair(NamedTuple):
    public_key: bytes
    private_key: bytes

class HybridKeyPair(NamedTuple):
    classical: KeyPair
    pqc: KeyPair

    def public_half(self) -> "HybridPublicKey":
        return HybridPublicKey(classical=self.classical.public_key, pqc=self.pqc.public_key)

class HybridPublicKey(NamedTuple):
    classical: bytes  # classical public key bytes
    pqc: bytes        # pqc public key bytes

class Challenge(NamedTuple):
    challenge_id: str       # unique identifier (UUID4)
    client_id: str          # identity of the requesting client
    nonce: bytes            # 32-byte random nonce (secrets.token_bytes)
    issued_at: float        # UTC timestamp from injected Clock
    expires_at: float       # issued_at + configured TTL

    def canonical_bytes(self, canonicalizer: "Canonicalizer") -> bytes:
        """Domain-separated canonical encoding for signing."""
        ...

class SessionToken(NamedTuple):
    session_id: str         # unique identifier (UUID4)
    client_id: str          # identity of the authenticated client
    created_at: float       # UTC timestamp from injected Clock
    expires_at: float       # created_at + session_ttl
    metadata: dict          # deployment-specific (e.g. granted scopes, IP, device fingerprint)

class PushChallenge(NamedTuple):
    challenge_id: str
    user_id: str
    device_id: str
    nonce: bytes
    issued_at: float
    expires_at: float

class EnrollmentResult(NamedTuple):
    user_id: str
    secret_uri: str         # otpauth:// URI for QR code generation
    backup_codes: list[str] # one-time recovery codes (if generated alongside enrollment)
```

**Wire serialization of `HybridPublicKey`:** when transmitted (e.g. during challenge-response), serialized as `[4-byte classical-pk-len][classical-pk-bytes][4-byte pqc-pk-len][pqc-pk-bytes]` — mirrors the signature wire format in §5.1 for consistency.

**`SessionToken` is opaque to clients.** Clients receive only `session_id` (an opaque string). The full `SessionToken` structure lives server-side in `KeyValueStore` — it is never serialized to the client, never signed into a JWT, and never trusted from wire data. Session validity is always checked by `orchestrator.validate(session_id)` which looks up the token from the store and checks `expires_at` against the injected `Clock`. This is a deliberate design choice: stateless tokens (JWTs) cannot be revoked without maintaining a revocation list that reintroduces server state anyway — QuantX skips the indirection and stores sessions directly.

### 3.9 `EventSink`
**Layer:** 0 — optional, injected where audit-trail emission is needed

**Outside:**
```python
class EventSink(Protocol):
    def emit(event_type: str, payload: dict, timestamp: float) -> None
        """Fire-and-forget audit event. Implementations must not raise — failures are swallowed or logged internally."""
```
**Why this exists:** a security-critical auth system needs observable events (challenge issued, verification succeeded/failed, session created/revoked, rate limit triggered). Rather than hardcoding a logging framework, `EventSink` follows the same DI pattern as every other Layer-0 interface — inject a `NullEventSink` (default, silent) for dev/test, a `StructuredLogEventSink` for production, or a custom implementation that writes to a SIEM.
**Connects to:** `SessionOrchestrator` (Layer 4), `PushAuthenticator` (Layer 5), `ThresholdManager` (Layer 8) — any component whose actions have security-audit significance accepts an optional `EventSink` in its constructor.

### 3.10 Exception Hierarchy
**Layer:** 0 — shared across all packages

```python
class QuantXError(Exception):
    """Base for all QuantX exceptions. Catch this to catch everything QuantX-specific."""

# --- Crypto-layer errors (Layers 1-2) ---
class CryptoError(QuantXError): """Base for cryptographic operation failures."""
class KeyGenerationError(CryptoError): """Key generation failed (e.g. entropy source unavailable)."""
class SignatureError(CryptoError): """Signing operation failed (distinct from verify returning False)."""
class EncapsulationError(CryptoError): """KEM encapsulate/decapsulate failed."""

# --- Storage-layer errors (Layers 0, 6) ---
class StorageError(QuantXError): """Base for storage/backend failures."""
class VaultCorruptedError(StorageError): """Persistent vault exists but fails integrity check."""
class BackendUnavailableError(StorageError): """Requested storage backend not available in this environment."""
class StoreCapacityError(StorageError): """KeyValueStore max_entries cap reached and entry could not be inserted."""

# --- Policy/protocol errors (Layers 3-4, 8) ---
class PolicyError(QuantXError): """Base for policy-violation rejections."""
class DuplicateParticipantKeyError(PolicyError): """Two threshold participants share a public key."""
class RegistryConfigError(PolicyError): """algorithm_registry.yaml is malformed, unsigned, or references unknown adapters."""
class ChallengeExpiredError(PolicyError): """Challenge TTL has elapsed."""
class RateLimitExceededError(PolicyError): """Request rejected by rate limiter."""
class ReplayRejectedError(PolicyError): """Token/challenge has already been consumed."""
```

**Rules:** `verify()` methods never raise — they return `False` on any failure (see §3.1 security notes). Exceptions above are for *operational* failures (entropy source down, HSM unreachable, corrupt vault) and *policy* rejections (rate limit, replay, expired challenge) — callers can distinguish "cryptographically invalid" (return value) from "system broken" (exception) without ambiguity.


---

## 4. Layer 1 — Algorithm Adapters (one atom per primitive)

Every row below is its own package (`algo-<name>`), implements exactly one Layer-0 interface, and contains no logic beyond calling one underlying library correctly. None of them know about "hybrid," "combiners," or each other.

| Component ID | Algorithm | Family | Implements | Wraps | Notes |
|---|---|---|---|---|---|
| `sig-classical-ed25519` | Ed25519 | classical | `Signer` | `cryptography.hazmat...ed25519` | Deterministic signatures, 32-byte keys, 64-byte sigs |
| `sig-classical-ecdsa-p256` | ECDSA/P-256 | classical | `Signer` | `cryptography` | Optional — for orgs whose HSMs/compliance regime mandate FIPS 186 ECDSA instead of EdDSA |
| `sig-pqc-mldsa65` | ML-DSA-65 (FIPS 204) | pqc | `Signer` | `liboqs` | Primary PQC signature algorithm |
| `sig-pqc-mldsa87` | ML-DSA-87 | pqc | `Signer` | `liboqs` | Higher-margin option for long-lived governance keys (see threshold-auth) |
| `sig-pqc-slhdsa` | SLH-DSA-SHA2-192f (FIPS 205) | pqc | `Signer` | `liboqs` | Structurally different (hash-based) — deliberate algorithmic diversity as a fallback if a future ML-DSA break is found |
| `kem-classical-x25519` | X25519 | classical | `KEMProvider` | `cryptography` | Modeled as a KEM via HKDF-wrapped ECDH per RFC 9180 §4.1 |
| `kem-pqc-mlkem768` | ML-KEM-768 (FIPS 203) | pqc | `KEMProvider` | `liboqs` | Primary PQC KEM |
| `kem-pqc-mlkem1024` | ML-KEM-1024 | pqc | `KEMProvider` | `liboqs` | High-assurance option |

**Signature-size caveat for SLH-DSA:** SLH-DSA-SHA2-192f produces signatures of approximately 35,664 bytes — roughly 550× larger than Ed25519's 64-byte signatures. This is inherent to hash-based signature schemes and is the trade-off for algorithmic diversity. Any deployment recipe enabling SLH-DSA should document this in its configuration notes, as some HTTP gateways, database columns, or message brokers may impose payload-size limits that reject SLH-DSA signatures silently. The wire format's 4-byte length fields (max ~4 GB) handle this without issue.

**Outside (identical shape for every row — this is the whole point):**
```
adapter = SigPqcMldsa65()
keypair = adapter.generate_keypair()          # -> KeyPair(public_key: bytes, private_key: bytes)
sig     = adapter.sign(message, keypair.private_key)
ok      = adapter.verify(message, sig, keypair.public_key)
```

**Inside (per adapter, ~30–60 lines each):** open the underlying library object, call the one relevant method, marshal bytes in/out, catch the library's own exceptions inside `verify()` and return `False`. Nothing else. If an adapter file is longer than that, something has leaked in that belongs in a different layer.

**Security notes:** because every adapter is this small and this uniform, a security reviewer can audit *all* of Layer 1 in an afternoon, and a new algorithm (say, a future NIST selection) ships as one new ~50-line file plus one new registry-YAML line — never a change to `SignatureCombiner`, `KEMCombiner`, `SessionOrchestrator`, or anything above.

**Connects to:** consumed only by Layer 2 combiners and Layer 3's `AlgorithmRegistry`. Never imported directly by Layer 4+ components — those only ever hold `Signer`/`KEMProvider`/`SignatureCombiner` interface references, resolved through the registry.


---

## 5. Layer 2 — Generic Combiners

There are exactly two components in this layer, total, for the whole system.

### 5.1 `SignatureCombiner`
**Layer:** 2 · **Depends on:** two `Signer` instances (any classical + any pqc, or any two at all) · **Implements:** `Signer`-shaped composite, but see below · **Fixes C1** · `GATE_REVIEW_REQUIRED = True`

**Outside:**
```
combiner = SignatureCombiner(classical=SigClassicalEd25519(), pqc=SigPqcMldsa65(),
                              required_mode=Mode.HYBRID)     # required_mode is fixed at construction, server-side, never from wire data

keypair = combiner.generate_keypair()          # -> HybridKeyPair(classical_kp, pqc_kp)
sig_bytes = combiner.sign(message, keypair)    # -> wire-format bytes, self-describing but see verify()

ok = combiner.verify(message, sig_bytes, keypair.public_half())
```
**Wire format:** `[1-byte declared-mode][4-byte classical-sig-len][classical-sig][4-byte pqc-sig-len][pqc-sig]` — either length field may be zero, meaning that component was omitted by the *signer* (used only for `PQC_ONLY` / `CLASSICAL_ONLY` operating modes that a deployment might legitimately choose).

**Inside — this is the actual C1 fix, spelled out:**
```
def verify(self, message, sig_bytes, public_keys) -> bool:
    parsed = self._parse(sig_bytes)                       # never trust more than "how do I split these bytes"
    if parsed.declared_mode != self.required_mode:         # <-- the fix: hard equality against SERVER config
        return False                                        #     not "declared mode says classical-only, so
                                                              #     I'll only check classical" like the old bug
    if self.required_mode in (Mode.HYBRID, Mode.PQC_ONLY):
        if not parsed.pqc_sig: return False
        if not self.pqc.verify(message, parsed.pqc_sig, public_keys.pqc): return False
    if self.required_mode in (Mode.HYBRID, Mode.CLASSICAL_ONLY):
        if not parsed.classical_sig: return False
        if not self.classical.verify(message, parsed.classical_sig, public_keys.classical): return False
    return True
```
Notice the difference from the old, broken version: **the branch taken is a function of `self.required_mode` (set once, server-side, at construction time), never of anything read from `sig_bytes`.** A signature declaring a mode other than what this specific `SignatureCombiner` instance was built for is rejected in the first line, full stop — there is no code path where an attacker's declared mode changes which cryptographic checks run.

**Security notes / non-goals:** this component enforces *mode*, not key freshness or replay — that's Layer 4's job (`ReplayStore`). A `SignatureCombiner` instance is single-purpose per policy: a session-orchestrator that needs to accept both a HYBRID-mode factor and, separately, a legacy CLASSICAL_ONLY factor during a migration window constructs **two** `SignatureCombiner` instances (one per `required_mode`) rather than one instance that's lenient about mode — this keeps the "never trust declared mode" invariant absolute rather than "usually enforced."

**Test obligation carried over from the audit:** every `SignatureCombiner` gets a mandatory test that (1) produces a real HYBRID signature, (2) strips the pqc component and rewrites the declared-mode byte to CLASSICAL_ONLY, (3) asserts `verify()` returns `False` against a combiner instance configured with `required_mode=HYBRID`. This exact test did not exist before and is now part of the component's own contract, not left to integration tests to remember.

### 5.2 `KEMCombiner`
**Layer:** 2 · **Depends on:** two `KEMProvider` instances · **Fixes M1** · `GATE_REVIEW_REQUIRED = True`

**Outside:**
```
combiner = KEMCombiner(classical=KemClassicalX25519(), pqc=KemPqcMlkem768())
ct_bundle, shared_secret = combiner.encapsulate(peer_public_keys)
shared_secret_2 = combiner.decapsulate(ct_bundle, my_private_keys)   # == shared_secret
```
**Inside:** `shared_secret = HKDF-Extract-and-Expand(salt=None, ikm=ss_classical || ss_pqc, info=domain_label || ct_classical || ct_pqc || pk_classical || pk_pqc)`. The addition of `ct_classical || ct_pqc || pk_classical || pk_pqc` into the KDF `info` field (vs. the old static-label-only design) is the entire M1 fix — it binds the derived secret to exactly which ciphertexts and public keys produced it, matching the X-Wing / RFC 9180-style combiner pattern, and prevents any scenario where mismatched or substituted ciphertexts on the two sides could go undetected.


---

## 6. Layer 3 — Algorithm Registry

### 6.1 `AlgorithmRegistry`
**Layer:** 3 · **Depends on:** a map of `role -> Signer|KEMProvider` instances, a `Canonicalizer`, an optional `Verifier` for its own config file · **Implements:** a role-lookup facade

**Outside:**
```
registry = AlgorithmRegistry.from_yaml("algorithm_registry.yaml", signing_key=ops_team_public_key)
signer_combiner = registry.get_signature_combiner(role="session-auth")   # -> configured SignatureCombiner
kem_combiner    = registry.get_kem_combiner(role="key-establishment")
```
**Wire/config format:** the same human-readable YAML the original project used (role → algorithm-family → adapter-id → security-level), with one addition addressing a gap the audit didn't rate as a live vulnerability but flagged for a "building block for hundreds of orgs": the YAML file is now expected to be **detached-signed** with an ops-team classical key (`registry.yaml.sig`), and `from_yaml()` refuses to load a config whose signature doesn't verify unless explicitly constructed with `allow_unsigned=True` (default `False` in any non-`dev` environment). This prevents a compromised config-management pipeline from silently downgrading an org's algorithm choices — the registry is a role-name-to-security-level mapping, and it's exactly the kind of file whose integrity should be treated the same way as the keys it points at.
**Inside:** parses YAML with `yaml.safe_load` only (never `yaml.load`), instantiates one Layer-1 adapter per line via a small `{adapter_id: class}` lookup table (the only place in the codebase that imports every Layer-1 adapter — everything else imports interfaces), and wraps role pairs in `SignatureCombiner`/`KEMCombiner` instances per role.

**Config schema — `algorithm_registry.yaml`:**
```yaml
# Each top-level key is a role name — a deployment-scoped label that higher layers
# use to request a configured combiner without naming specific algorithms.
roles:
  session-auth:                      # primary authentication flow
    signature:
      classical: Ed25519             # must match a registered adapter's algorithm_id
      pqc: ML-DSA-65
      mode: HYBRID                   # HYBRID | PQC_ONLY | CLASSICAL_ONLY
    kem:
      classical: X25519
      pqc: ML-KEM-768

  session-auth-pqc-only:             # PQC-only variant (Recipe C)
    signature:
      pqc: ML-DSA-87
      mode: PQC_ONLY

  governance-signing:                # threshold-auth use case
    signature:
      classical: ECDSA-P256          # for orgs with FIPS 186 HSM mandates
      pqc: ML-DSA-87                 # higher security margin for long-lived governance keys
      mode: HYBRID

  key-establishment:                 # KEM role for session key derivation
    kem:
      classical: X25519
      pqc: ML-KEM-768

  key-establishment-high:            # high-assurance KEM variant
    kem:
      classical: X25519
      pqc: ML-KEM-1024
```
**Required fields:** `roles.<name>.signature` or `roles.<name>.kem` (at least one). Within `signature`: `mode` is required; `classical` and `pqc` are required or optional depending on `mode` (e.g. `PQC_ONLY` requires `pqc` only). Within `kem`: both `classical` and `pqc` are required (KEM combination is always hybrid — there is no "classical-only KEM" mode). Every `algorithm_id` value must match exactly one registered Layer-1 adapter; unknown IDs cause `RegistryConfigError` at load time, not at first use.
**Connects to:** everything from Layer 4 upward asks the registry for a combiner by role name; nothing above Layer 3 ever names a specific algorithm.

---

## 7. Layer 4 — Session/Protocol Primitives

### 7.1 `ChallengeIssuer`
**Layer:** 4 · **Depends on:** `Clock`, `Canonicalizer`, `KeyValueStore` (to persist outstanding challenges so this is stateless-safe across instances)

**Outside:**
```
challenge = issuer.issue(client_id: str, client_ip: str) -> Challenge
# Challenge = { challenge_id, client_id, nonce, issued_at, expires_at }
canonical_bytes = challenge.canonical_bytes()      # delegates to injected Canonicalizer — never formats JSON itself
```
**Inside:** random 32-byte nonce via `secrets.token_bytes`; domain-separated canonical encoding (`b"QUANTX-CHALLENGE-V2:" + canonicalizer.canonicalize({...})`) so a challenge can never be confused with any other signed structure in the system, even by accident.

### 7.2 `SessionOrchestrator`
**Layer:** 4 · **Depends on:** `ChallengeIssuer`, `Clock`, `ReplayStore`, `RateLimiter` (one per-identity + one global instance, per Principle 8), `SignatureCombiner`, `KeyValueStore` (for session tokens) · **Fixes C1 (enforcement point), H1, H2, M4**

**Outside:**
```python
orchestrator = SessionOrchestrator(challenge_issuer, replay_store, per_id_limiter, global_limiter,
                                    signature_combiner, session_store, session_ttl=3600)
challenge = orchestrator.start(client_id, client_ip)
token = orchestrator.finish(challenge.challenge_id, signed_response: bytes, public_keys, client_ip)
valid = orchestrator.validate(session_id) -> bool
orchestrator.revoke(session_id)
```
**Inside (order of operations, each step a hard gate to the next):**
1. `global_limiter.check_and_record(...)` — volumetric abuse check, key-rotation-proof (Principle 8 / H1).
2. `per_id_limiter.check_and_record(client_id, ...)` — per-identity throttle.
3. `replay_store.consume_once(challenge_id, ttl)` — atomic; second concurrent call for the same challenge_id always loses here, closing the race the audit specifically checked for.
4. Look up the `Challenge` from `session_store` (not a private in-process dict — this alone is the H2 fix: any orchestrator instance behind any load balancer node can complete a challenge issued by any other node).
5. `clock.now() < challenge.expires_at` — reject expired challenges before any cryptographic work. Raises `ChallengeExpiredError`.
6. `signature_combiner.verify(...)` — mode-enforced per the C1 fix in §5.1; nothing below this line runs if this fails.
7. **Only after every one of the above has passed** is a `SessionToken` constructed and written to `session_store`. (This is the M4 fix — compare to the old reference server, which minted a token, then verified a second factor, then revoked on failure; if the second-factor check raised instead of returning `False`, revocation was skipped. In v2, nothing is written to the store until every gate has already returned successfully — there is no token to leak because none was ever created on a failure path, exceptions included.)
**Security notes:** `SessionOrchestrator` never imports a specific algorithm adapter or a specific `KeyValueStore` backend — swap `InMemoryKVStore` for `RedisKVStore` in the wiring code and the exact same orchestrator class is now cluster-safe.


---

## 8. Layer 5 — Authentication Factors

### 8.1 `TotpProvider`
**Layer:** 5 · **Depends on:** `Clock`, `KeyValueStore` (replaces the old unbounded in-process `_used_steps` set), `RateLimiter`

**Outside:** unchanged from the original design (it was one of the better-built modules in the audit) — `enroll(user_id) -> EnrollmentResult`, `verify_code(user_id, code) -> bool`.
**Inside (what changed):** the used-step replay set is now `KeyValueStore.set_if_not_exists(f"totp-used:{user_id}:{step}", ttl=period*(drift_window+2))` instead of an in-process `set()` — bounded by the shared store's cap, and cluster-safe. Rate limiting was already correct; unchanged.
**Security notes (carried over, still true):** TOTP is a phishable second factor by design (the user can be tricked into typing a valid code into an attacker's proxy). Document this plainly wherever `TotpProvider` is offered as an option in a deployment recipe — it is not a substitute for the hybrid-signature factor, only a companion to it.

### 8.2 `PushAuthenticator`
**Layer:** 5 · **Depends on:** `Clock`, `KeyValueStore`, `RateLimiter`, `ReplayStore` · **Fixes H3, M5**

**Outside:** `issue_push_challenge(user_id, device_id) -> PushChallenge`, `verify_push_approval(challenge_id, signature, public_key) -> bool`.
**Inside (what changed):**
- `issue_push_challenge` now calls `rate_limiter.check_and_record(f"push:{user_id}", limit=3, window_seconds=300)` before creating anything — closes H3 (push-bombing/MFA-fatigue), using the exact same generic `RateLimiter` component every other factor uses, not a bespoke one.
- `verify_push_approval` calls `replay_store.consume_once(challenge_id, ttl)` as its first step and only proceeds to signature verification if that returns `True` — closes M5 (the old version allowed the same valid signature to be replayed against the same challenge repeatedly within its TTL).


---

## 9. Layer 6 — Key Custody

### 9.1 `KeyWallet` (orchestrator)
**Layer:** 6 · **Depends on:** a `StorageBackend` interface (below), `Canonicalizer`

**Outside:** `store(key_id, keypair, metadata) -> None`, `retrieve(key_id) -> KeyPair`, `rotate(key_id) -> KeyPair`, `list_keys() -> list[KeyMeta]`.
**Inside:** pure orchestration — serializes/deserializes key material to a backend-agnostic envelope and delegates everything else. Contains zero storage logic itself, which is what makes the backends below truly swappable.

### 9.2 `StorageBackend` interface
```
class StorageBackend(Protocol):
    capability: Literal["software-encrypted", "os-native", "hardware"]   # honest, machine-readable claim
    def store_key(key_id: str, key_bytes: bytes, metadata: dict) -> None
    def retrieve_key(key_id: str) -> tuple[bytes, dict]
    def delete_key(key_id: str) -> None
```

### 9.3 `EncryptedFileBackend`
**Layer:** 6 · Implements `StorageBackend`, `capability = "software-encrypted"` · **Fixes M3**

**Inside (what changed from the audited version — everything else about it was already sound: AES-256-GCM, 600k-iteration PBKDF2-SHA256, per-entry random salt+nonce, atomic tmp-file+replace):**
- The AES-GCM **AAD now covers `key_id || canonicalizer.canonicalize(metadata)`**, not just `key_id` — tampering with any metadata field (version, role, algorithm label) now invalidates the authentication tag, closing the "attacker with file access can rewrite metadata undetected" gap.
- `_read_store()` now distinguishes three outcomes instead of two: `Ok(data)`, `NotFound` (file legitimately doesn't exist yet — fine, returns empty store), and `Corrupted` (file exists but fails to parse — **raises** `VaultCorruptedError` instead of silently returning `{}`). A corrupted vault can no longer masquerade as "no keys were ever stored here."

### 9.4 `OSKeychainBackend`
**Layer:** 6 · Implements `StorageBackend`, `capability = "os-native"` · **Fixes H4**

**Inside:** now a real integration (`keyring` library → macOS Keychain / Windows Credential Manager / Linux Secret Service, selected automatically by the underlying library), not a Python dict. If the underlying OS keychain service is unavailable in a given environment (e.g. headless Linux with no Secret Service daemon running), the constructor **raises `BackendUnavailableError` at wiring time** rather than silently falling back to an in-memory dict — a deployment finds out immediately at startup that it needs a different backend, instead of discovering months later that "OS-protected" keys were never actually OS-protected.
**This backend is no longer the default anywhere.** `KeyWallet()` requires an explicit `backend=` argument; there is no silent default, precisely because the audit's worst key-custody finding was a *default* that lied about its own guarantees.

### 9.5 `HsmPkcs11Backend`
**Layer:** 6 · Implements `StorageBackend`, `capability = "hardware"` · **Fixes H4** · `GATE_REVIEW_REQUIRED = True`

**Inside:** a real `python-pkcs11` integration against a configured PKCS#11 module path and slot/PIN. If no real HSM/PKCS#11 module is configured, this component **does not exist as a usable object** — its factory function raises `NotImplementedError("no PKCS#11 module configured; see docs/hsm-setup.md")` rather than shipping a mock that pretends to be hardware-backed. Building a real HSM integration is explicitly out of scope for this document (it depends entirely on which HSM vendor a given org uses) — what v2 fixes is not "add fake HSM support," it's "stop claiming to have HSM support until there's a real PKCS#11 call underneath it."

---

## 10. Layer 7 — Recovery

### 10.1 `BackupCodeManager`
**Layer:** 7 · Depends on: `KeyValueStore`. Unchanged from the audited design — the entropy reasoning (12 chars over a 32-symbol alphabet ≈ 2^60, justifying a single fast salted SHA-256 instead of a slow KDF) was correct and is kept as-is.

### 10.2 `DeviceLinker`
**Layer:** 7 · Depends on: `SignatureCombiner` (injected — this component has no crypto logic of its own), `ReplayStore`
**Inside (what changed):** because it now depends on the fixed, generic `SignatureCombiner` from §5.1 instead of the old ad hoc `hybrid_verify`, the downgrade bug (C1) is fixed here automatically — this is the payoff of Principle 3 (generic combiners): one fix, propagated everywhere the interface is used, with no separate patch needed for this module. Adds `replay_store.consume_once(pairing_token, ttl)` so a pairing assertion can't be replayed to link a second rogue device using an intercepted approval.

---

## 11. Layer 8 — Governance (Threshold Auth)

### 11.1 `ThresholdPolicy`
**Layer:** 8 · Depends on: `Canonicalizer` · **Fixes M6**
**Outside:** `create_policy(participants: list[Participant], threshold: int) -> Policy`
**Inside (what changed):** `create_policy` now rejects (raises `DuplicateParticipantKeyError`) if any two `Participant` entries share a `classical_public_key` or `pqc_public_key` — closing the "one physical key registered as two participants to satisfy a 2-of-N threshold alone" gap. This check is a single `len(set(...)) == len(...)` assertion; trivial to implement, meaningful to skip.

### 11.2 `ThresholdManager`
**Layer:** 8 · Depends on: `ThresholdPolicy`, `SignatureCombiner` (one per participant's chosen algorithm — participants may use different algorithms from each other; the manager doesn't care, it just asks each participant's own combiner to verify their partial signature), `Canonicalizer`
**Outside:** unchanged shape (`propose`, `submit_partial_signature`, `finalize_decision`) — the fix is entirely inside `ThresholdPolicy`, not here, which is the point of keeping these as two separate atomic pieces instead of one.

---

## 12. Layer 9 — Privacy / Membership Proofs

### 12.1 `MerkleMembershipProof` — sound, honestly non-anonymous
**Layer:** 9 · Depends on: hash function (SHA-256), `Canonicalizer` · **Fixes C2 (soundness half)** · `GATE_REVIEW_REQUIRED = True`

**Outside:**
```
directory = MembershipDirectory()
directory.add_member(member_id, salt)
proof = prover.generate_proof(statement, witness)
ok = verifier.verify_proof(statement, proof)     # <-- now actually recomputes the path
```
**Inside — the actual C2 soundness fix:** `verify_proof()` walks `proof.merkle_path` starting from `proof.leaf_commitment`, applying `hash_nodes(current, sibling)` in the direction specified at each step, and asserts the final value **equals `statement.root`**. This single missing loop — present in the old prover's internal helper but never called by the old verifier — is what makes this a real proof instead of decoration. `response_proof` is likewise recomputed by the verifier from `(challenge, blinding_factor, leaf_commitment)` — which means `blinding_factor` must now travel as part of the proof (it was withheld in the old, broken design in a way that made the "response" uncheckable by anyone). Removing that field from the proof's payload is the actual "commitment-reveal" step of a proper Fiat–Shamir transform.
**Security notes — read this before using it for anything sensitive:** this component proves *real* membership. It does **not** hide *which* member is proving membership from the verifier — `merkle_path` reveals the exact tree position, and any verifier who also knows the directory's member ordering can identify the prover. Label every deployment recipe that uses this component "authenticated, non-anonymous membership check" — never "anonymous" or "zero-knowledge" in user-facing copy. If genuine anonymity is a requirement, use §12.2 instead.

### 12.2 `AnonymousProofBackend` — pluggable interface, deliberately unimplemented here
**Layer:** 9 · `GATE_REVIEW_REQUIRED = True`, and additionally: **not shipped with a reference implementation in this document.**
```
class AnonymousProofBackend(Protocol):
    def prove_membership(statement, witness) -> bytes     # must not reveal witness position
    def verify_membership(statement, proof: bytes) -> bool
```
**Why this is intentionally a bare interface:** real anonymous set-membership proofs (Semaphore-style nullifier schemes, or an actual zk-STARK circuit over the Merkle path) require either a vetted circuit library (e.g. `circom`+`snarkjs`, Halo2, or a STARK toolkit like Winterfell/RISC0) or a from-scratch construction that gets independent cryptographic review before it touches a single real credential. Shipping a homemade approximation was exactly the old C2 bug. v2's answer is: define the interface precisely, wire every consumer against the interface only, and treat "which vetted library implements it" as a decision made at deployment time — with an explicit gate that a real ZK cryptographer signs off before `GATE_REVIEW_REQUIRED` is cleared to `False` for a specific implementation.


---

## 13. Layer 10 — Observability & Compliance

### 13.1 `CryptoBOMModel`
**Layer:** 10 — pure data model (a "CBOM entry": location, algorithm, key size, role, discovered-by). No logic. Every scanner below produces a stream of these; every reporter below consumes a stream of these. This is the shared vocabulary that lets scanners and reporters be swapped independently.

### 13.2 `StaticSourceScanner`
**Layer:** 10 — regex/keyword based, unchanged approach from the audited version. **Its `README` must state plainly, as a permanent header, that it produces best-effort results with real false positives/negatives** — this was flagged as a documentation-honesty gap, not a code bug, and the fix is documentation discipline, not new logic.

### 13.3 `TlsInspector`
**Layer:** 10 · **Fixes M7**
**Inside (what changed):** the scanner now performs **two** distinct probes, clearly labeled in its output: an **authenticated probe** (default `ssl.create_default_context()`, real certificate validation, real hostname checking) that reports "confirmed" cipher/protocol/certificate data only when the handshake is genuinely trusted; and an explicitly opt-in **permissive probe** (`CERT_NONE`, for scanning known-self-signed internal endpoints) whose output is tagged `"trust": "unverified"` in every `CryptoBOMModel` entry it produces, so a compliance report can never accidentally present network-attacker-controllable data as a verified finding. It also now actually parses the fetched certificate (`cryptography.x509.load_der_x509_certificate`) to report the leaf certificate's own signature algorithm and key size — closing the "fetches the cert, never reads it" gap.

### 13.4 `StandardsCatalog`
**Layer:** 10 — pure data: FIPS 203/204/205, CNSA 2.0, NIST IR 8547 mappings, each entry tagged `status: "final" | "draft"`. Unchanged — this was one of the best-executed pieces of the original codebase (the draft-disclaimer discipline was consistently correct) and is kept as-is.

### 13.5 `ComplianceReportGenerator`
**Layer:** 10 · Depends on: a stream of `CryptoBOMModel` entries, `StandardsCatalog`, `Canonicalizer`. Pure consumer/renderer — no scanning logic, no standards data of its own. Swap in a different `StandardsCatalog` (say, a future post-quantum standard) with zero changes here.

---

## 14. Composition Recipes — proving the Lego claim

Every recipe below is *only wiring* — constructor calls passing interface implementations to each other. No recipe requires editing a single component's internals.

### Recipe A — Minimal single-process demo
```
clock          = SystemClock()
kv             = InMemoryKVStore(max_entries=10_000)
canon          = JCSCanonicalizer()
registry       = AlgorithmRegistry.from_yaml("algorithm_registry.yaml", allow_unsigned=True)  # dev only
sig_combiner   = registry.get_signature_combiner("session-auth")           # Ed25519 + ML-DSA-65, HYBRID required
replay         = ReplayStore(kv)
limiter_id     = RateLimiter(kv)
limiter_global = RateLimiter(kv)
orchestrator   = SessionOrchestrator(ChallengeIssuer(clock, canon, kv), replay,
                                      limiter_id, limiter_global, sig_combiner, kv)
totp           = TotpProvider(clock, kv, RateLimiter(kv))
wallet         = KeyWallet(backend=EncryptedFileBackend(path="./dev-vault.enc", passphrase=...))
```

### Recipe B — Enterprise, multi-instance, horizontally scaled
Same code as Recipe A, with exactly these substitutions — nothing else in the wiring or in any component changes:
```
kv       = RedisKVStore(url="redis://cluster.internal:6379")
registry = AlgorithmRegistry.from_yaml("algorithm_registry.yaml", signing_key=ops_pubkey)   # signed config required
wallet   = KeyWallet(backend=HsmPkcs11Backend(module_path=..., slot=..., pin_from_env=...))
threshold_manager = ThresholdManager(ThresholdPolicy(canon), sig_combiner)   # for wire-transfer-style approvals
push     = PushAuthenticator(clock, kv, RateLimiter(kv), ReplayStore(kv))    # added as a second-factor option
```

### Recipe C — Compliance-sensitive / PQC-only
```
sig_combiner = registry.get_signature_combiner("session-auth-pqc-only")   # registry role configured with required_mode=PQC_ONLY
# every other component identical to Recipe A — PushAuthenticator and TotpProvider are simply not wired in,
# since this recipe's threat model excludes any online/phishable factor.
```

---

## 15. Audit Finding → Fix Traceability

| Finding | Severity | v2 Component(s) | How it's structurally closed |
|---|---|---|---|
| C1 — hybrid downgrade | Critical | `SignatureCombiner` (§5.1) | `required_mode` is server-set at construction; wire-declared mode is checked, never trusted |
| C2 — zkp-module verifies nothing | Critical | `MerkleMembershipProof` (§12.1), `AnonymousProofBackend` (§12.2) | Verifier now actually walks the path to the root; anonymity isolated behind a gated, unimplemented-by-default interface |
| H1 — unbounded in-memory DoS | High | `InMemoryKVStore` (§3.5), `RateLimiter` global instance (§3.7) | Hard `max_entries` cap + eviction at the one shared primitive everything else is built on |
| H2 — no horizontal scaling | High | `KeyValueStore` interface + `RedisKVStore` (§3.5) | Every stateful component depends on the interface, not a concrete store |
| H3 — push-bombing | High | `PushAuthenticator` (§8.2) | `RateLimiter` gate added before challenge issuance |
| H4 — fake HSM/keychain backends | High | `OSKeychainBackend`, `HsmPkcs11Backend` (§9.4–9.5) | Real integrations or explicit `NotImplementedError`/`BackendUnavailableError`; no silent dict default |
| M1 — KEM combiner doesn't bind ct/pk | Medium | `KEMCombiner` (§5.2) | ciphertexts + public keys added to HKDF `info` |
| M2 — ad hoc JSON canonicalization | Medium | `JCSCanonicalizer` (§3.3) | RFC 8785 implemented once, injected everywhere |
| M3 — vault metadata not authenticated / corruption swallowed | Medium | `EncryptedFileBackend` (§9.3) | Metadata included in AES-GCM AAD; corruption raises instead of returning empty |
| M4 — session minted before all factors pass | Medium | `SessionOrchestrator` (§7.2) | Token write is the last statement after every gate, no exception path can leave a live token |
| M5 — push approval replay | Medium | `PushAuthenticator` (§8.2) | `ReplayStore.consume_once` gate |
| M6 — threshold policy key reuse | Medium | `ThresholdPolicy` (§11.1) | Duplicate-key rejection at policy creation |
| M7 — TLS inspector disables cert verification, never parses cert | Medium | `TlsInspector` (§13.3) | Split authenticated/permissive probes, results tagged by trust level, cert actually parsed |
| L1 — falsy-zero timestamp bug | Low | `Clock` interface (§3.4) | Injected clock removes the `x or default` pattern entirely — callers pass explicit values, no sentinel confusion |
| L2 — scanner false positive/negative honesty | Low | `StaticSourceScanner` (§13.2) | Documentation requirement, not a code change |

---

## 16. Build Checklist — Gate Reviews Required Before Production

Components flagged `GATE_REVIEW_REQUIRED = True` above, in the order a real cryptographer should look at them:
1. `SignatureCombiner` (§5.1) — verify the mode-enforcement invariant holds under every wire-format edge case (truncated bytes, oversized length fields, both components present but one malformed).
2. `KEMCombiner` (§5.2) — confirm the HKDF binding construction against the current draft of whatever hybrid-KEM RFC is authoritative at build time.
3. `ThresholdManager` / `ThresholdPolicy` (§11) — review the finalize/quorum logic for any signature-malleability or double-counting edge case beyond the key-uniqueness fix already made.
4. `MerkleMembershipProof` (§12.1) — confirm the Fiat–Shamir transform is sound for this exact statement/witness structure, and that the non-anonymity caveat is impossible to miss in any UI that surfaces this feature.
5. Whatever concrete implementation is eventually plugged into `AnonymousProofBackend` (§12.2) — full external audit before `GATE_REVIEW_REQUIRED` is cleared for that specific implementation, not just this interface.

Nothing in this list is optional before "hundreds of orgs" — but note that, unlike the v1 codebase, a reviewer here can look at exactly five small, isolated components instead of needing to re-derive the security properties of the whole platform, because every other component's correctness no longer depends on these five getting it right.
