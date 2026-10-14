# Datadog Setup for QuantX

## Purpose

Datadog is useful for metrics, logs, and traces when running the REST sidecar or multi-instance deployments (Phase 4+).

## Student Offer

Claim the Datadog student / Pro account via the GitHub Student Developer Pack.

## Setup Steps

1. Create a Datadog account.
2. Generate an API key and Application key.
3. Store them in 1Password.
4. For local or CI use, inject via environment variables:

```env
DD_API_KEY=...
DD_APP_KEY=...
DD_SITE=datadoghq.com
DD_ENV=development
DD_SERVICE=quantx
```

## When to Integrate

- After a runnable service exists
- When you need visibility into latency, error rates, or resource usage
- Not required for pure library development or unit tests

## Notes

Keep the integration optional and behind configuration so the core packages remain lightweight.
