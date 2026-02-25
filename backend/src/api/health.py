"""
Health check API endpoint.

Provides system health status for monitoring and load balancers.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any
import logging
from src.config import settings
from src.database import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    checks: Dict[str, Any]


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status with component checks

    Checks:
        - Database connectivity
        - Configuration validity
    """
    checks = {}

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # Check configuration
    try:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        checks["config"] = {"status": "healthy"}
    except Exception as e:
        logger.error(f"Config health check failed: {str(e)}")
        checks["config"] = {"status": "unhealthy", "error": str(e)}

    # Determine overall status
    overall_status = "healthy"
    for check in checks.values():
        if check["status"] == "unhealthy":
            overall_status = "unhealthy"
            break

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        checks=checks
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/load balancers.

    Returns:
        200 if ready, 503 if not ready
    """
    try:
        # Check database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not ready", "error": str(e)}, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes.

    Returns:
        200 if alive
    """
    return {"status": "alive"}
