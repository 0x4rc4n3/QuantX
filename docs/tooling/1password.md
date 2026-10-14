# 1Password Setup for QuantX

## Why

1Password (free for 1 year via GitHub Student Developer Pack) is the recommended way to store development secrets, API keys, and local credentials.

## Setup Steps

1. Claim the 1Password offer from the [GitHub Student Developer Pack](https://education.github.com/pack).
2. Create a vault (e.g. `QuantX-Dev`).
3. Store items such as:
   - Sentry DSN
   - Datadog API / App keys
   - Any local test private keys (never production keys)
   - GitHub tokens used for automation

## Usage Patterns

- Use 1Password CLI (`op`) to inject secrets into local shells when needed.
- Never commit `.env` files containing real values.
- Reference secrets from GitHub Actions via repository Secrets (Settings → Secrets and variables → Actions).

## Recommended Items to Store

| Item | Purpose |
|------|--------|
| `SENTRY_DSN` | Error monitoring |
| `DD_API_KEY` / `DD_APP_KEY` | Datadog (if used) |
| Local test key material | Development only |
| Personal access tokens | CI / automation |

## Rule

If a value would be damaging if leaked, it belongs in 1Password (or GitHub Secrets), never in the repository.
