"""FastAPI application entry point for QuantX REST sidecar.

Layer: sidecar
Depends on: quantx_service.wiring.build_app_dependencies, quantx_service.routers, quantx_service.middleware, quantx_service.errors
Implements: FastAPI application instance, router mounting, middleware installation, and exception handlers
Outside: Endpoint business logic and cryptographic operations
Inside: Application assembly, router attachment, middleware configuration, and exception mapping
Security notes: Installs HybridTLSEnforcementMiddleware and RateLimitHeadersMiddleware to enforce transport security and uniform rate limiting.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from quantx_core.exceptions.backend_unavailable_error import BackendUnavailableError
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.exceptions.replay_detected_error import ReplayDetectedError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.config import ServiceConfig
from quantx_service.errors.already_consumed_error import (
    AlreadyConsumedError,
    already_consumed_handler,
)
from quantx_service.errors.backend_unavailable_error import (
    BackendUnavailableHTTPError,
    backend_unavailable_handler,
)
from quantx_service.errors.error_envelope import create_error_response
from quantx_service.errors.malformed_request_error import (
    MalformedRequestError,
    malformed_request_handler,
)
from quantx_service.errors.not_found_error import NotFoundError, not_found_handler
from quantx_service.errors.rate_limited_error import (
    RateLimitedHTTPError,
    rate_limited_handler,
)
from quantx_service.errors.verification_failed_error import (
    VerificationFailedError,
    verification_failed_handler,
)
from quantx_service.middleware.hybrid_tls_enforcement import HybridTLSEnforcementMiddleware
from quantx_service.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from quantx_service.routers import challenge_router, session_router, verify_router
from quantx_service.wiring import AppDependencies, build_app_dependencies, set_global_dependencies


def create_app(
    config: ServiceConfig | None = None,
    dependencies: AppDependencies | None = None,
) -> FastAPI:
    """Create and assemble the FastAPI application instance."""
    app = FastAPI(
        title="QuantX REST Sidecar",
        description="PQC Authentication REST Sidecar",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )

    if dependencies is not None:
        set_global_dependencies(dependencies)
    elif config is not None:
        build_app_dependencies(config)

    # Register Exception Handlers
    app.add_exception_handler(MalformedRequestError, malformed_request_handler)
    app.add_exception_handler(VerificationFailedError, verification_failed_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AlreadyConsumedError, already_consumed_handler)
    app.add_exception_handler(ReplayDetectedError, already_consumed_handler)
    app.add_exception_handler(RateLimitedHTTPError, rate_limited_handler)
    app.add_exception_handler(RateLimitedError, rate_limited_handler)
    app.add_exception_handler(BackendUnavailableHTTPError, backend_unavailable_handler)
    app.add_exception_handler(BackendUnavailableError, backend_unavailable_handler)
    app.add_exception_handler(MalformedInputError, malformed_request_handler)

    @app.exception_handler(RequestValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return create_error_response(
            status_code=400,
            code="malformed_request",
            message="Request body or query parameter validation failed",
            details=exc.errors(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            return create_error_response(
                status_code=404,
                code="not_found",
                message=str(exc.detail or "Resource not found"),
            )
        return create_error_response(
            status_code=exc.status_code,
            code="malformed_request" if exc.status_code == 400 else "internal_error",
            message=str(exc.detail),
        )

    # Mount routers
    app.include_router(challenge_router.router)
    app.include_router(verify_router.router)
    app.include_router(session_router.router)

    # Install middleware
    tls_mode = config.service.get("tls_enforcement", "off") if config else "off"
    app.add_middleware(HybridTLSEnforcementMiddleware, tls_enforcement=tls_mode)
    app.add_middleware(RateLimitHeadersMiddleware)

    return app


app = create_app()
