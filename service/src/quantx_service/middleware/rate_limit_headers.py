"""Rate limit headers ASGI middleware.

Layer: sidecar
Depends on: quantx_core.exceptions.rate_limited_error.RateLimitedError
Implements: ASGI middleware ensuring Retry-After and rate-limit headers are attached to 429 responses
Outside: Rate limiting evaluation and policy enforcement (handled by Layer 0 RateLimiter)
Inside: Response interception and Retry-After header injection on 429 responses
Security notes: Ensures consistent, machine-readable rate-limit backoff guidance per 08-api-specification.md.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable


class RateLimitHeadersMiddleware:
    """Middleware attaching Retry-After headers to 429 rate-limited responses."""

    def __init__(self, app: Any, default_retry_after: int = 60) -> None:
        self.app = app
        self.default_retry_after = default_retry_after

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                status = message.get("status")
                if status == 429:
                    headers = list(message.get("headers", []))
                    has_retry_after = any(k.lower() == b"retry-after" for k, v in headers)
                    if not has_retry_after:
                        headers.append(
                            (b"retry-after", str(self.default_retry_after).encode("ascii"))
                        )
                        message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
