"""
Health Check API Routes
Provides system health and readiness endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time

from app.schemas.common import HealthResponse, HealthStatus, ServiceHealth
from app.database.postgres import get_db
from app.database.mongodb import get_mongodb
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    mongodb = Depends(get_mongodb)
):
    """
    Comprehensive health check endpoint
    Checks all critical services
    """
    services = {}
    overall_status = HealthStatus.HEALTHY
    
    # Check PostgreSQL
    try:
        start = time.time()
        await db.execute("SELECT 1")
        latency = (time.time() - start) * 1000
        services["postgresql"] = ServiceHealth(
            status=HealthStatus.HEALTHY,
            latency_ms=round(latency, 2),
            message="Connected"
        )
    except Exception as e:
        services["postgresql"] = ServiceHealth(
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )
        overall_status = HealthStatus.UNHEALTHY
    
    # Check MongoDB
    try:
        start = time.time()
        await mongodb.client.admin.command('ping')
        latency = (time.time() - start) * 1000
        services["mongodb"] = ServiceHealth(
            status=HealthStatus.HEALTHY,
            latency_ms=round(latency, 2),
            message="Connected"
        )
    except Exception as e:
        services["mongodb"] = ServiceHealth(
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )
        overall_status = HealthStatus.UNHEALTHY
    
    # API itself is healthy if we got here
    services["api"] = ServiceHealth(
        status=HealthStatus.HEALTHY,
        message="Running"
    )
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services,
        version="1.0.0"
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe
    Returns 200 if service is ready to accept traffic
    """
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    Returns 200 if service is alive
    """
    return {"alive": True}
