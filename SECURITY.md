# Security Policy

## Supported Versions

QuantX is currently in active development (pre-production).

| Version | Supported |
|---------|-----------|
| main (development) | :white_check_mark: Security fixes accepted |
| Released packages | Not yet available |

## Reporting a Vulnerability

**Do not open public GitHub issues for security vulnerabilities.**

Please report security issues privately:

- Email: mudassirbhatti276@gmail.com
- Or open a private security advisory on this repository (GitHub Security Advisories)

Include as much detail as possible:
- Description of the issue
- Steps to reproduce
- Potential impact
- Any suggested fix (optional)

You should receive an acknowledgement within 72 hours.

## Security Principles (Non-Negotiable)

- No hand-rolled cryptographic primitives. Only established libraries (`cryptography`, `liboqs`).
- Hybrid classical + PQC is the default posture.
- Mode is a server-side construction fact, never trusted from the wire.
- Fail closed on verification failures.
- Secrets must never appear in logs, source control, or client responses.
- `GATE_REVIEW_REQUIRED` components must not be called production-ready until independently reviewed.

## liboqs Disclaimer

liboqs is a research/prototyping library. Its maintainers do not currently recommend it for protecting sensitive data in production. QuantX mitigates this by requiring hybrid mode by default and by keeping PQC backends swappable.

## Preferred Secrets Management

Use a password manager / secrets manager (e.g. 1Password) for local development secrets. In CI and deployment, use GitHub Actions secrets or equivalent environment-based injection. Never hard-code secrets.
