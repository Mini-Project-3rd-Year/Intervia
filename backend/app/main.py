"""
Intervia Backend — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.api.v1 import api_v1_router
from app.api.v1.ws_interview import router as ws_interview_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    setup_logging()
    logger = get_logger()
    settings = get_settings()

    logger.info(
        "Intervia API starting",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
    )

    yield

    # Shutdown
    logger.info("Intervia API shutting down")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="Intervia API",
        description=(
            "AI-powered adaptive interview and career coaching platform. "
            "Built with FastAPI, LangGraph, and Gemini."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ---- CORS middleware -----------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ---- Register routers ---------------------------------
    app.include_router(api_v1_router)
    app.include_router(ws_interview_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.BACKEND_RELOAD,
        log_level="debug" if settings.DEBUG else "info",
    )
