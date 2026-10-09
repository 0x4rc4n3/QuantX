# `hybrid_tls_enforcement.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Enforces the sidecar's required hybrid TLS 1.3 group (X25519MLKEM768) at the transport boundary — the sidecar-level analogue of SR-1's mode enforcement, applied to the transport layer rather than the application-layer signature.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service/middleware/`
- **Depends on:** `config.py` (this package, for the configured TLS requirement)
- **Imported by:** `main.py` (installed as ASGI middleware)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `config.py`
- **Implements:** ASGI middleware inspecting/enforcing the negotiated TLS group.
- **Outside:** Application-layer signature mode enforcement — that's SR-1 inside `SignatureCombiner`, a separate concern from transport-layer TLS.
- **Inside:** Rejecting connections that did not negotiate the required hybrid group. TLS terminates inside this service's own process (D-016), so the negotiated group is read from the live connection with no proxy header to trust.
- **Security notes:** This is the transport-layer half of the system's overall no-silent-downgrade posture — SR-1 covers the application-layer signature, this covers the TLS layer.

## Required behavior
- Enforces the required hybrid TLS 1.3 group (X25519MLKEM768) per `08-api-specification.md`, at whatever point in the stack TLS-negotiation details are visible to this middleware.
- Rejects connections that didn't negotiate the required group, when the deployment's TLS termination point makes that information available to the application layer.

## Inputs / outputs
- **In:** the negotiated TLS connection's group information (where visible).
- **Out:** pass-through on the required group; rejection otherwise.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A connection whose negotiated group cannot be read is rejected (fail closed).

## Security notes
- Transport-layer analogue of SR-1 — a downgraded TLS group is a downgrade attack the same way a stripped PQC signature component is.

## Mandatory tests this must pass
- Exercised indirectly via `service/tests/` integration tests where the test environment can simulate TLS negotiation; unit-testable in isolation for the group-checking logic itself.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.

## Explicitly out of scope for this file
- Application-layer signature mode enforcement — Layer 2's SR-1.

## Source docs
`08-api-specification.md`
