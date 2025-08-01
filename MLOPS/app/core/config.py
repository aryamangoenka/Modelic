"""
Configuration management for MLOps Platform
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings with environment variable support."""
    
    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True
    
    # GitHub Integration
    github_webhook_secret: str = ""
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Celery/Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Logging
    log_level: str = "INFO"
    
    # Storage
    model_storage_path: str = "/tmp/mlops_models"
    repo_storage_path: str = "/tmp/mlops_repos"
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Drift Detection Configuration (Phase 2.2)
    drift_psi_threshold: float = 0.2
    drift_kl_divergence_threshold: float = 0.1
    drift_check_interval_hours: int = 24
    drift_min_samples: int = 30
    drift_max_features: int = 50
    drift_enable_auto_check: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            fastapi_host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
            fastapi_port=int(os.getenv("FASTAPI_PORT", "8000")),
            fastapi_reload=os.getenv("FASTAPI_RELOAD", "true").lower() == "true",
            github_webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET", ""),
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            celery_broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
            celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            model_storage_path=os.getenv("MODEL_STORAGE_PATH", "/tmp/mlops_models"),
            repo_storage_path=os.getenv("REPO_STORAGE_PATH", "/tmp/mlops_repos"),
            # Drift detection settings
            drift_psi_threshold=float(os.getenv("DRIFT_PSI_THRESHOLD", "0.2")),
            drift_kl_divergence_threshold=float(os.getenv("DRIFT_KL_DIVERGENCE_THRESHOLD", "0.1")),
            drift_check_interval_hours=int(os.getenv("DRIFT_CHECK_INTERVAL_HOURS", "24")),
            drift_min_samples=int(os.getenv("DRIFT_MIN_SAMPLES", "30")),
            drift_max_features=int(os.getenv("DRIFT_MAX_FEATURES", "50")),
            drift_enable_auto_check=os.getenv("DRIFT_ENABLE_AUTO_CHECK", "true").lower() == "true",
        )


# Global settings instance
settings = Settings.from_env() 