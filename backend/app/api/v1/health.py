"""
Intervia Backend — Health Check Endpoint
GET /api/v1/health
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the current health status of the Intervia API service.",
)
async def health_check() -> HealthResponse:
    """
    Simple health check endpoint.
    Used by load balancers, Docker healthchecks, and CI pipelines.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="intervia-api",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )
