# QuantX v2 Architecture Contract

**Version:** 2.0.0-draft.2  
**Status:** Normative implementation contract for the AI-builder phase; not a security audit or production approval.  
**Authority:** This document replaces the unavailable `QuantX-v2-Architecture.md` referenced by earlier scaffold documents. Any future revision must increment the version and update the decision log.

## 1. Scope and conformance

This document fixes the public shapes, serialization rules, and reference service boundaries that were previously left to inference. A builder must implement the rules here unless a newer version is explicitly accepted in `docs/DECISIONS.md`. A component that cannot conform must stop and report the conflict.

This contract does not certify the cryptographic primitives, third-party libraries, implementation, or deployment. All `GATE_REVIEW_REQUIRED` components remain subject to independent review.

Normative terms have their ordinary standards meaning: **MUST**, **MUST NOT**, **SHOULD**, and **MAY** indicate required, prohibited, recommended, and optional behavior.

## 2. Canonical repository and package boundaries

The repository is a Python 3.11+ monorepo with the ten publishable packages listed in `14-directory-structure.md`. Each package has a `src/<snake_case_module>/` layout, its own `pyproject.toml`, and a test tree. Dependencies point from higher layers to lower layers only. `AlgorithmRegistry` is the single permitted exception to the Layer-1 adapter import rule.

The sidecar under `service/` is an optional FastAPI/ASGI application. It depends on published package interfaces and is not imported by library packages.

## 3. Foundational public interfaces

The following signatures are normative. `bytes` values are opaque byte strings unless a section below assigns a serialization. Implementations MUST raise a typed error or return the documented failure value; they MUST NOT silently coerce malformed input.

| Interface | Required public methods | Failure rule |
|---|---|---|
| `Signer` | `sign(message: bytes) -> bytes` | Backend failures raise an explicit exception. |
| `Verifier` | `verify(message: bytes, signature: bytes) -> bool` | Malformed input returns `False`; it MUST NOT escape from verification. |
| `KEMProvider` | `encapsulate(public_key: bytes) -> tuple[bytes, bytes]`; `decapsulate(ciphertext: bytes, private_key: bytes) -> bytes` | Malformed input or decapsulation failure raises a typed error at the adapter boundary and becomes a failed verification/handshake at the orchestration boundary. |
| `Canonicalizer` | `canonicalize(data: Mapping[str, object]) -> bytes` | Non-canonicalizable data raises a typed input error. |
| `Clock` | `now() -> datetime` | Returned datetimes MUST be timezone-aware UTC values. |
| `KeyValueStore` | `get(key: str) -> bytes \| None`; `set(key: str, value: bytes, ttl: TTL \| None = None) -> None`; `delete(key: str) -> None` | Backend failure raises `BackendUnavailableError`; no silent in-memory fallback. |
| `ReplayStore` | `consume_once(key: str, ttl: TTL) -> bool` | `True` only for the first successful consume; later calls return `False`. |
| `RateLimiter` | `allow(identity_key: str) -> bool` | Every call is counted according to the configured window; no unbounded state. |

All constructors MUST receive these interfaces through dependency injection. They MUST NOT read system time, create module-level mutable state, or instantiate sibling concrete implementations.

## 4. Modes and registry

`Mode` is a string-backed enum with exactly these values:

| Enum member | Wire/config value | Required component count |
|---|---|---:|
| `HYBRID` | `HYBRID` | 2: one classical and one PQC component |
| `PQC_ONLY` | `PQC_ONLY` | 1 PQC component |
| `CLASSICAL_ONLY` | `CLASSICAL_ONLY` | 1 classical component |

`required_mode` is fixed by the server-side registry role at construction. A client or wire message MAY carry a diagnostic declared mode, but it MUST NOT override `required_mode`. A mismatch is a failed request before cryptographic verification begins.

A registry role is represented as a mapping with the required fields `role_id: str`, `mode: Mode`, `signature_algorithms: list[str]`, and `kem_algorithms: list[str]`. Lists MUST be non-empty, MUST contain no duplicates, and MUST match the mode. Production configuration MUST be signed; unsigned configuration is permitted only in an explicitly marked development recipe.

## 5. Versioned signature wire format

Signature containers use this exact binary format. All integers are unsigned big-endian. No trailing bytes are accepted.

```text
SignatureContainer =
    version       : u8       # MUST be 0x01
    mode          : u8       # 0x01 HYBRID, 0x02 PQC_ONLY, 0x03 CLASSICAL_ONLY
    component_cnt : u8       # MUST equal 2 for HYBRID, otherwise 1
    component[]   : component_cnt * SignatureComponent

SignatureComponent =
    algorithm_id_len : u16
    algorithm_id     : UTF-8 bytes, length 1..64
    signature_len    : u32
    signature        : bytes, length 1..1_048_576
```

The component order is the registry order and is part of the signed/verified meaning. Hybrid containers MUST contain exactly one classical and one PQC component. Algorithm identifiers MUST be ASCII-compatible UTF-8, lower-case, and match the registry exactly. The parser MUST reject version, mode, count, length, UTF-8, duplicate-algorithm, ordering, trailing-byte, and maximum-size violations with `MalformedInputError`. It MUST never allocate based on an unchecked length.

The parser returns an immutable record containing `version`, `mode`, and an ordered tuple of `(algorithm_id, signature_bytes)`. It does not decide whether the mode is permitted; that is `signature_mode_enforcement.py`.

## 6. Versioned KEM wire format

KEM containers use the same envelope discipline and exact binary rules:

```text
KEMContainer =
    version       : u8       # MUST be 0x01
    mode          : u8       # same values as SignatureContainer
    component_cnt : u8       # MUST equal 2 for HYBRID, otherwise 1
    component[]   : component_cnt * KEMComponent

KEMComponent =
    algorithm_id_len : u16
    algorithm_id     : UTF-8 bytes, length 1..64
    public_key_len   : u32
    public_key       : bytes, length 1..1_048_576
    ciphertext_len   : u32
    ciphertext       : bytes, length 1..1_048_576
```

Components are ordered by the registry. The parser rejects all malformed, duplicate, out-of-order, oversized, unsupported, mismatched, and trailing data. `public_key` and `ciphertext` are retained as separate fields because both MUST be passed into the HKDF binding function.

## 7. KEM combination and binding contract

`kem_hkdf_binding.derive()` MUST use the standard `cryptography` HKDF implementation with SHA-256, `length=32`, and `salt=None`. It MUST construct the `info` value exactly as:

```text
info = b"QuantX-KEM-v1\x00" ||
       u8(component_count) ||
       repeat(component_count times in registry order:
           u16(len(algorithm_id)) || algorithm_id_utf8 ||
           u32(len(public_key)) || public_key ||
           u32(len(ciphertext)) || ciphertext)
```

The HKDF input key material is the concatenation of shared secrets in registry order. The resulting 32 bytes are the derived combined key. Length and count bounds from the KEM wire format apply before HKDF is called. Any mismatch in component count, algorithm order, or mode is a failure. This construction remains `GATE_REVIEW_REQUIRED` and requires independent review and known-answer vectors before production use.

## 8. Signature combination contract

For `HYBRID`, verification MUST succeed only when both the classical and PQC component verifications succeed. For single-mode operation, exactly the one component required by the mode is verified. The message passed to every component verifier is the same caller-supplied message after one canonicalization step when the caller supplies structured data.

**Signed payload (D-009, accepted).** Every component signature is computed over `b"QuantX-SIG-v1\x00" || u8(mode) || u16(len(role_id)) || role_id || u32(len(message)) || message`, built from the canonicalized message. ML-DSA uses `context=None`. Signature golden vectors, including cross-role and cross-mode replay cases, are written against this construction.

The combiner MUST reject a mode or algorithm set that differs from the server-side registry role before invoking a component verifier. It MUST treat malformed containers and unknown algorithms as verification failure at the public verification boundary.

## 9. Session and authentication contract

The reference session flow is:

1. `ChallengeIssuer` creates a single-use challenge with a server-generated nonce, subject binding, role binding, issue time, and expiry.
2. The client submits the signed/combined response and the challenge identifier.
3. `SessionOrchestrator.start()` validates challenge state, replay state, rate limits, and signature/KEM requirements.
4. TOTP/HOTP, push, and recovery gates execute according to the configured policy, each with independent replay/rate-limit state.
5. `SessionOrchestrator.finish()` records successful gate completion.
6. `SessionOrchestrator.validate()` returns a `SessionToken` only after every required gate succeeds.

A token MUST NOT be minted on any exception path. Challenge and approval identifiers MUST be consumed through `ReplayStore` exactly once.

## 10. Reference REST sidecar contract

The sidecar uses FastAPI and exposes these paths:

| Method | Path | Responsibility |
|---|---|---|
| `POST` | `/v1/challenges` | Issue a challenge for an authenticated subject and registry role. |
| `POST` | `/v1/verify` | Verify a signed/combined response under server-selected mode. |
| `POST` | `/v1/sessions` | Start or finish the configured authentication flow. |
| `GET` | `/healthz` | Process health only; it MUST NOT disclose secrets or verification state. |

The JSON error envelope is:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "request_id": "string"
  }
}
```

`message` MUST be safe for clients and MUST NOT contain private key material, raw tokens, or untrusted input without encoding. Authentication failures, malformed input, replay, rate limiting, unavailable backends, and not-found cases map to stable error codes documented by the service error modules. Internal logs may include diagnostics under a request identifier.

The reference deployment terminates TLS at the ASGI process or at a trusted proxy that passes an authenticated, non-spoofable negotiated-group header. If the application cannot cryptographically trust the proxy assertion, the middleware MUST fail closed rather than infer the TLS group. The networked sidecar MUST NOT serve plaintext HTTP, including in development. In-process ASGI tests MAY use a test client without a network transport because no external connection is being accepted.

## 11. Test-vector and compatibility requirements

The builder MUST add golden vectors for:

- Each mode and valid signature container.
- Every signature-container malformed-input class.
- Each mode and valid KEM container.
- Every KEM-container malformed-input class.
- HKDF binding with one and two components.
- Ciphertext substitution and public-key substitution.
- Registry-order changes and duplicate algorithms.

The following minimum vectors are normative smoke vectors. They are intentionally small and do not represent real cryptographic signatures or KEM outputs.

| Case | Input or encoded bytes | Expected result |
|---|---|---|
| Classical signature container | `01030100076564323535313900000002aabb` | Decode as version `1`, `CLASSICAL_ONLY`, one component with algorithm `ed25519` and signature `aabb`. |
| Classical KEM container | `010301000678323535313900000002aabb00000003010203` | Decode as version `1`, `CLASSICAL_ONLY`, one `x25519` component with public key `aabb` and ciphertext `010203`. |
| One-component HKDF binding | Shared secret `101112131415161718191a1b1c1d1e1f`, algorithm `x25519`, public key `aabb`, ciphertext `010203` | `eb43f2e06a96f73985f6094525595cc8a68e8036352724ddc54e516e2963e025`. |

The HKDF vector uses the exact `info` encoding in §7, SHA-256, no salt, and 32-byte output. The test suite MUST independently recompute the vector using `cryptography` rather than trusting a copied expected value alone.

**Erratum (draft.2).** In draft.1 the two container smoke vectors above each carried one stray `00` byte directly after the 3-byte header and did not parse under §5/§6 (the `algorithm_id_len` field read as `0x0000`). They are corrected here; the HKDF vector was unchanged and was independently recomputed with `cryptography` and matches. The test suite must still parse both container vectors with the real parser and recompute the HKDF vector independently.

The wire format version byte is the compatibility boundary. A future incompatible format MUST use a new version and MUST NOT reinterpret version `0x01`. Implementations MUST reject unknown versions.

## 12. Remaining review requirements

This contract closes the missing-document gap, but it does not make implementation safe by itself. Independent review remains mandatory for combiners, HKDF binding, registry, wallet backends, threshold components, and membership-proof components. The PQC backend statement (D-006) remains mandatory, and `cryptography` is bounded to `>=48,<51` (D-010). No component is production-ready until its implementation, tests, vectors, dependency review, and independent sign-off are complete.

## References

[1]: docs/06-system-architecture.md "QuantX system architecture"
[2]: docs/08-api-specification.md "QuantX REST API specification"
[3]: docs/10-security-requirements.md "QuantX security requirements"
[4]: docs/13-error-and-edge-cases.md "QuantX error and edge-case requirements"
[5]: docs/14-directory-structure.md "QuantX canonical directory structure"
[6]: docs/DECISIONS.md "QuantX decision log"
