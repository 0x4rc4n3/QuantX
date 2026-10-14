# Sentry Setup for QuantX

## Purpose

Sentry provides error tracking and performance monitoring. Useful once the REST sidecar or any long-running service exists.

## Student Offer

Claim the Sentry student plan via the [GitHub Student Developer Pack](https://education.github.com/pack).

## Setup Steps

1. Create a Sentry account and a new project (platform: Python).
2. Copy the DSN.
3. Store the DSN in 1Password and as a GitHub Actions secret named `SENTRY_DSN` (when needed).
4. Add to local `.env` (never commit it):

```env
SENTRY_DSN=https://<key>@o<org>.ingest.sentry.io/<project>
SENTRY_ENVIRONMENT=development
```

## Integration (when code is ready)

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    traces_sample_rate=0.1,
)
```

## Notes

- Do not send private keys, passwords, or full credential material to Sentry.
- Use before-send hooks later to scrub sensitive fields if needed.
- Enable only after you have a runnable service; pure library packages usually do not need Sentry.
