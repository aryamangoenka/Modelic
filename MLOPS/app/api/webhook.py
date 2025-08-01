"""
GitHub webhook API endpoints
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.core.schemas import GitHubWebhookPayload, WebhookResponse
from app.services.github_service import GitHubService
from app.services.model_service import ModelService
from app.core.exceptions import ModelProcessingError, RepositoryError, ModelValidationError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["GitHub Integration"])

# Dependencies
github_service = GitHubService()
model_service = ModelService()

# Global variable to hold main app reference (set during startup)
_main_app = None

def set_main_app(app):
    """Set the main app reference for model deployment."""
    global _main_app
    _main_app = app


@router.post("/webhook", response_model=WebhookResponse)
async def github_webhook(payload: GitHubWebhookPayload):
    """
    GitHub webhook endpoint for handling push events.
    
    This endpoint:
    1. Validates the GitHub push payload
    2. Clones the repository to a temporary directory
    3. Validates the model repository structure
    4. Triggers model validation and deployment
    
    Expected repository structure:
    - model.pkl or model.pt (trained model file)
    - requirements.txt (Python dependencies)
    - predict.py (inference function)
    - test_data.json (sample input for validation)
    """
    logger.info(
        f"Received GitHub webhook for repo: {payload.repository.full_name}, "
        f"ref: {payload.ref}, commit: {payload.head_commit.id if payload.head_commit else 'None'}"
    )
    
    try:
        # Step 1: Validate webhook payload
        is_valid, reason = github_service.validate_webhook_payload(payload.dict())
        
        if not is_valid:
            return WebhookResponse(
                status="skipped",
                message=reason
            )
        
        # Step 2: Extract repository information
        repo_info = github_service.extract_repository_info(payload.dict())
        repo_url = repo_info["repo_url"]
        repo_name = repo_info["repo_name"]
        full_name = repo_info["full_name"]
        
        # Step 3: Clone repository
        cloned_repo_path = await github_service.clone_repository(repo_url, repo_name)
        
        # Step 4: Deploy model using model service
        deployment_result = await model_service.deploy_model(
            repo_name=repo_name,
            github_repo=full_name,
            repo_path=cloned_repo_path,
            main_app=_main_app
        )
        
        logger.info(
            f"Successfully processed webhook for {full_name}, "
            f"deployed model {deployment_result['model_id']} at {deployment_result['endpoint_url']}"
        )
        
        return WebhookResponse(
            status="success",
            message=f"Model {repo_name} deployed successfully",
            model_id=deployment_result["model_id"],
            deployment_url=deployment_result["endpoint_url"]
        )
        
    except ModelValidationError as e:
        logger.error(f"Model validation failed for {payload.repository.full_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": f"Model validation failed: {str(e)}", "trace": None}
        )
    except ModelProcessingError as e:
        logger.error(f"Model processing failed for {payload.repository.full_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Model processing failed: {str(e)}", "trace": None}
        )
    except RepositoryError as e:
        logger.error(f"Repository operation failed for {payload.repository.full_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Repository error: {str(e)}", "trace": None}
        )
    except Exception as e:
        logger.error(
            f"Webhook processing failed for {payload.repository.full_name}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "trace": type(e).__name__}
        ) 