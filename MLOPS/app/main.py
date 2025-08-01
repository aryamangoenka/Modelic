"""
MLOps Platform - Main FastAPI Application
Streamlined main app with modular structure.
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    ModelValidationError, ModelProcessingError, RepositoryError, ModelDeploymentError
)
from app.api import health, webhook, models
from app.services.model_service import ModelService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="MLOps Platform API",
    description="Automated ML model deployment and monitoring platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Set main app reference for webhook service
    webhook.set_main_app(app)
    
    # Initialize database and load data
    from app.db.database import init_inference_logs, init_drift_reports, init_baseline_stats
    logs_count = init_inference_logs()
    logger.info(f"Loaded {logs_count} inference logs from storage")

    drift_reports_count = init_drift_reports()
    logger.info(f"Loaded {drift_reports_count} drift reports from storage")
    
    baseline_stats_count = init_baseline_stats()
    logger.info(f"Loaded {baseline_stats_count} baseline statistics from storage")
    
    # Reload models from registry
    model_service = ModelService()
    reload_result = await model_service.reload_models_from_registry(app)
    
    logger.info(f"Model reload result: {reload_result}")
    logger.info("MLOps Platform API startup completed")
    
    # Start scheduled drift detection service (Phase 2.2)
    try:
        from app.services.scheduled_drift_service import scheduled_drift_service
        await scheduled_drift_service.start_scheduler()
        logger.info("Started automated drift detection scheduler")
    except Exception as e:
        logger.warning(f"Failed to start drift detection scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown."""
    try:
        from app.services.scheduled_drift_service import scheduled_drift_service
        await scheduled_drift_service.stop_scheduler()
        logger.info("Stopped drift detection scheduler")
    except Exception as e:
        logger.warning(f"Error stopping drift detection scheduler: {e}")


# Exception handlers
@app.exception_handler(ModelValidationError)
async def model_validation_exception_handler(request: Request, exc: ModelValidationError):
    logger.error(f"Model validation failed: {str(exc)} for path: {request.url.path}")
    raise HTTPException(
        status_code=422,
        detail={"error": f"Model validation failed: {str(exc)}", "trace": None}
    )


@app.exception_handler(ModelProcessingError)
async def model_processing_exception_handler(request: Request, exc: ModelProcessingError):
    logger.error(f"Model processing failed: {str(exc)} for path: {request.url.path}")
    raise HTTPException(
        status_code=500,
        detail={"error": f"Model processing failed: {str(exc)}", "trace": None}
    )


@app.exception_handler(RepositoryError)
async def repository_exception_handler(request: Request, exc: RepositoryError):
    logger.error(f"Repository operation failed: {str(exc)} for path: {request.url.path}")
    raise HTTPException(
        status_code=400,
        detail={"error": f"Repository error: {str(exc)}", "trace": None}
    )


@app.exception_handler(ModelDeploymentError)
async def deployment_exception_handler(request: Request, exc: ModelDeploymentError):
    logger.error(f"Model deployment failed: {str(exc)} for path: {request.url.path}")
    raise HTTPException(
        status_code=500,
        detail={"error": f"Model deployment failed: {str(exc)}", "trace": None}
    )


# Include API routers
app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(models.router, prefix="/models")

# Note: Individual model prediction endpoints are created dynamically
# via the ModelService when models are deployed

logger.info("MLOps Platform API initialized successfully")


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
        log_level=settings.log_level.lower()
    ) 