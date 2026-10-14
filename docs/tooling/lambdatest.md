# LambdaTest / BrowserStack Notes

## Purpose

Cross-browser and mobile testing platforms. Relevant only if QuantX later includes a web UI, admin console, or browser-based demo.

## Student Offer

Both LambdaTest and BrowserStack frequently appear in the GitHub Student Developer Pack. Claim the one you prefer.

## Current Recommendation

**Do not integrate yet.**

QuantX is currently focused on Python packages and an optional REST sidecar. There is no browser UI that requires cross-browser testing.

Revisit this document only when:
- A web-based admin or demo UI is added, or
- You need to verify browser wallet / extension behavior across browsers.

## If You Need It Later

1. Claim the student plan.
2. Store access credentials in 1Password.
3. Add credentials as GitHub Actions secrets if used in CI.
4. Keep tests optional so local development does not depend on an external service.
