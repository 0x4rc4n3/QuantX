# `errors/` — sidecar error mapping

## What this is
`error_envelope.py`'s shared JSON shape, plus one file per error kind mapping a library exception (or a request-validation failure) onto the correct HTTP status code, per `08-api-specification.md`'s error model.

## Part of
`service`, the REST sidecar.

## Contains
- `error_envelope.py` — the shared response shape
- `malformed_request_error.py` — `400 malformed_request`
- `verification_failed_error.py` — `401 verification_failed`
- `not_found_error.py` — `404 not_found`
- `already_consumed_error.py` — `409 already_consumed`
- `rate_limited_error.py` — `429 rate_limited`
- `backend_unavailable_error.py` — `503 backend_unavailable`

## Why divided this way
One error kind per file, per `14-directory-structure.md`'s atomicity rule — each maps exactly one Layer-0/library exception (or validation failure) to exactly one HTTP status, so the mapping table is auditable file-by-file.

## Dependency rules
- Every file here depends on `error_envelope.py` for its response shape.
- Each error file maps to at most one underlying library exception — no file handles more than one HTTP status code.

## Source docs
`08-api-specification.md`, `14-directory-structure.md`
