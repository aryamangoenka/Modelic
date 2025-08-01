"""
Pydantic models for request/response validation
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field


# GitHub Webhook Models
class GitHubRepository(BaseModel):
    """GitHub repository information from webhook payload."""
    id: int
    name: str
    full_name: str
    clone_url: str
    default_branch: str = "main"


class GitHubCommit(BaseModel):
    """GitHub commit information from webhook payload."""
    id: str
    message: str
    author: Dict[str, Any]
    modified: List[str] = Field(default_factory=list)
    added: List[str] = Field(default_factory=list)


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload structure for push events."""
    ref: str
    repository: GitHubRepository
    head_commit: Optional[GitHubCommit] = None
    commits: List[GitHubCommit] = Field(default_factory=list)


# Response Models
class WebhookResponse(BaseModel):
    """Standard response for webhook processing."""
    status: str
    message: str
    model_id: Optional[str] = None
    deployment_url: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    trace: Optional[str] = None
    timestamp: str


# Model API Models
class PredictionRequest(BaseModel):
    """Standard prediction request format."""
    data: Dict[str, Any]


class PredictionResponse(BaseModel):
    """Standard prediction response format."""
    prediction: Any
    confidence: Optional[float] = None
    model_version: str
    inference_time_ms: int
    model_id: str


# Health Check Models
class HealthResponse(BaseModel):
    """Health check response format."""
    status: str
    version: str
    services: Dict[str, str]
    registered_models: int


class ModelHealthResponse(BaseModel):
    """Model health check response format."""
    status: str
    model_id: str
    ready_for_inference: bool
    error: Optional[str] = None
    last_checked: float


# Model Management Models
class ModelInfo(BaseModel):
    """Model information response format."""
    model_id: str
    name: str
    version: str
    status: str
    github_repo: str
    created_at: str
    updated_at: str
    endpoint_path: str
    predict_endpoint: str
    info_endpoint: str


class ModelListResponse(BaseModel):
    """Model list response format."""
    models: List[Dict[str, Any]]
    total_count: int
    status: str 