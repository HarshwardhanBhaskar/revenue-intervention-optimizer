"""
Revenue Intervention Optimizer — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from api import dashboard, opportunities, actions, experiments, policies, audit, assistant, webhooks
from middleware.request_id import RequestIdMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)

    # Initialize database tables
    from models.database import init_db
    await init_db()

    yield

    # Cleanup on shutdown


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-powered revenue recovery with incremental intervention optimization",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate Limiting & DoS Protection Middleware (120 req/min, 1MB max payload)
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute * 2,
        max_content_length=1_048_576,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Tracing Middleware
    app.add_middleware(RequestIdMiddleware)

    # API routes
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(opportunities.router, prefix="/api/opportunities", tags=["Opportunities"])
    app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])
    app.include_router(experiments.router, prefix="/api/experiments", tags=["Experiments"])
    app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
    app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
    app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])

    @app.get("/health")
    async def health():
        return {"status": "healthy", "app": settings.app_name}

    return app


app = create_app()
