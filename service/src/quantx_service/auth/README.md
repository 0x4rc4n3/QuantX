# `auth/` — sidecar client authentication

## What this is
Two alternative mechanisms for authenticating the sidecar's *client* (a calling service), not the end-user subject QuantX's challenge/response flow authenticates.

## Part of
`service`, the REST sidecar.

## Contains
- `bearer_token_auth.py` — static/rotating bearer token
- `mtls_auth.py` — mutual TLS client certificate

## Why divided this way
Two structurally different mechanisms a deployment picks between based on its own TLS termination setup, per `09-auth-and-authorization.md`.

## Dependency rules
- Neither imports the other — a deployment wires whichever one `config.py` selects.

## Source docs
`09-auth-and-authorization.md`, `14-directory-structure.md`
