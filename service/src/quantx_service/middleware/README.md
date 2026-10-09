# `middleware/` — sidecar ASGI middleware

## What this is
Two pieces of cross-cutting ASGI middleware: hybrid-TLS enforcement (transport-layer downgrade protection) and rate-limit header attachment.

## Part of
`service`, the REST sidecar.

## Contains
- `hybrid_tls_enforcement.py` — transport-layer analogue of SR-1
- `rate_limit_headers.py` — `Retry-After` header attachment

## Why divided this way
Two unrelated cross-cutting concerns, kept in separate files per `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- Neither middleware imports the other; both are installed independently in `main.py`.

## Source docs
`08-api-specification.md`, `14-directory-structure.md`
