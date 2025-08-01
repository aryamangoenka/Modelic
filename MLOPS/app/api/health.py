"""
Health check API endpoints
"""

import logging
from fastapi import APIRouter

from app.core.schemas import HealthResponse
from app.db.database import init_supabase
from app.models.registry import get_registered_models

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/", response_model=dict)
async def root():
    """Platform welcome endpoint."""
    return {
        "message": "MLOps Platform API is running", 
        "version": "0.1.0",
        "status": "healthy"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check with system status."""
    # Check database connection
    supabase_status = "connected" if init_supabase() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "api": "running",
            "database": supabase_status,
            "redis": "pending"  # Will be implemented with Celery
        },
        registered_models=len(get_registered_models())
    ) 