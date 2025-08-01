"""
Model service for handling model lifecycle operations
"""

import logging
from pathlib import Path
from typing import Dict, Any

from app.core.exceptions import ModelProcessingError, ModelValidationError
from app.db.database import (
    create_model_record, update_model_status, create_deployment_record,
    ModelStatus, ModelMetadata
)
from app.models.loader import validate_model_repository
from app.models.registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelService:
    """Service for handling model lifecycle operations."""
    
    def __init__(self):
        self.registry = ModelRegistry()
    
    async def deploy_model(
        self,
        repo_name: str,
        github_repo: str,
        repo_path: Path,
        main_app
    ) -> Dict[str, Any]:
        """
        Deploy a model from a repository.
        
        Args:
            repo_name: Repository name
            github_repo: Full GitHub repository name
            repo_path: Path to the cloned repository
            main_app: FastAPI main application instance
            
        Returns:
            Deployment result with model_id and endpoint_url
            
        Raises:
            ModelProcessingError: If deployment fails
        """
        try:
            # Step 1: Validate repository structure and model
            validation_result = await validate_model_repository(repo_path)
            
            if not validation_result["structure_valid"]:
                raise ModelValidationError(f"Invalid repository structure: {validation_result['structure_errors']}")
            
            if not validation_result.get("model_validation_passed", False):
                error_msg = validation_result.get("model_validation_error", "Unknown model validation error")
                raise ModelValidationError(f"Model validation failed: {error_msg}")
            
            # Step 2: Create model record in database
            model_metadata = await create_model_record(
                name=repo_name,
                github_repo=github_repo,
                model_file_path=str(repo_path / validation_result.get("model_file", "model.pkl")),
                predict_file_path=str(repo_path / "predict.py"),
                requirements_path=str(repo_path / "requirements.txt"),
                test_data_path=str(repo_path / "test_data.json")
            )
            
            logger.info(f"Created model record: {model_metadata.id}")
            
            # Step 3: Register dynamic API for this model
            endpoint_url = await self._register_model_api(model_metadata, repo_path, main_app)
            
            # Step 3.5: Create baseline statistics from test data (Phase 2.1)
            try:
                from app.db.database import create_baseline_from_test_data
                await create_baseline_from_test_data(
                    model_id=model_metadata.id,
                    test_data_path=str(repo_path / "test_data.json")
                )
                logger.info(f"Created baseline statistics for model {model_metadata.id}")
            except Exception as baseline_error:
                logger.warning(f"Failed to create baseline statistics for model {model_metadata.id}: {baseline_error}")
                # Don't fail deployment if baseline creation fails
            
            # Step 4: Update model status to deployed
            await update_model_status(model_metadata.id, ModelStatus.DEPLOYED)
            
            # Step 5: Create deployment record
            deployment_record = await create_deployment_record(
                model_id=model_metadata.id,
                endpoint_url=endpoint_url,
                version=model_metadata.version
            )
            
            logger.info(f"Successfully deployed model {model_metadata.id} at {endpoint_url}")
            
            return {
                "model_id": model_metadata.id,
                "endpoint_url": endpoint_url,
                "deployment_record": deployment_record
            }
            
        except (ModelValidationError, Exception) as e:
            # Update model status to failed if we have a model_id
            if 'model_metadata' in locals():
                await update_model_status(model_metadata.id, ModelStatus.FAILED)
            
            logger.error(f"Failed to deploy model: {e}")
            raise ModelProcessingError(f"Failed to deploy model: {str(e)}")
    
    async def _register_model_api(
        self,
        model_metadata: ModelMetadata,
        repo_path: Path,
        main_app
    ) -> str:
        """
        Register model API endpoints.
        
        Args:
            model_metadata: Model metadata
            repo_path: Path to the model repository
            main_app: FastAPI main application instance
            
        Returns:
            Endpoint URL for the model
        """
        # Import here to avoid circular imports
        from app.models.dynamic_api import ModelAPI
        
        try:
            # Create model API
            model_api = ModelAPI(model_metadata, repo_path)
            
            # Create unique path for this model
            model_path = f"/models/{model_metadata.id}"
            
            # Include the router in the main app
            main_app.include_router(
                model_api.router,
                prefix=model_path,
                tags=[f"Model: {model_metadata.name}"]
            )
            
            # Store in registry
            endpoint_url = f"{model_path}/predict"
            ModelRegistry.register_model(
                model_metadata=model_metadata,
                api_instance=model_api,
                repo_path=repo_path,
                endpoint_url=endpoint_url
            )
            
            logger.info(f"Registered model API: {endpoint_url}")
            return endpoint_url
            
        except Exception as e:
            logger.error(f"Failed to register model API: {e}")
            raise ModelProcessingError(f"Failed to register model API: {str(e)}")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed model information.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model information dictionary
        """
        model_data = ModelRegistry.get_model_data(model_id)
        
        if not model_data:
            return {"error": f"Model {model_id} not found"}
        
        # Model data is stored directly in the registry, not under a "metadata" key
        return {
            "model_id": model_data["model_id"],
            "name": model_data["name"],
            "version": model_data["version"],
            "status": model_data["status"],
            "github_repo": model_data["github_repo"],
            "created_at": model_data["created_at"],
            "updated_at": model_data["updated_at"],
            "endpoint_path": f"/models/{model_data['model_id']}",
            "predict_endpoint": f"/models/{model_data['model_id']}/predict",
            "info_endpoint": f"/models/{model_data['model_id']}/info",
            "health_endpoint": f"/models/{model_data['model_id']}/health",
            "registered_at": model_data["registered_at"]
        }
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all deployed models.
        
        Returns:
            List of models with metadata
        """
        registered_models = ModelRegistry.get_registered_models()
        
        return {
            "models": list(registered_models.values()),
            "total_count": len(registered_models),
            "status": "success"
        }
    
    async def reload_models_from_registry(self, main_app) -> Dict[str, Any]:
        """
        Reload all models from registry on startup.
        
        Args:
            main_app: FastAPI main application instance
            
        Returns:
            Reload result with count of reloaded models
        """
        try:
            registered_models = ModelRegistry.get_registered_models()
            reloaded_count = 0
            failed_count = 0
            
            logger.info(f"Attempting to reload {len(registered_models)} models from registry")
            
            for model_id, model_data in registered_models.items():
                try:
                    # Check if repo path still exists
                    repo_path = Path(model_data.get("repo_path", ""))
                    if not repo_path.exists():
                        logger.warning(f"Repository path not found for model {model_id}: {repo_path}")
                        failed_count += 1
                        continue
                    
                    # Create ModelMetadata object from registry data
                    from app.db.database import ModelMetadata, ModelStatus
                    from datetime import datetime
                    
                    metadata = ModelMetadata(
                        id=model_data["model_id"],
                        name=model_data["name"],
                        version=model_data["version"],
                        status=ModelStatus(model_data["status"]),
                        github_repo=model_data["github_repo"],
                        model_file_path=str(repo_path / "model.pkl"),  # Default path
                        predict_file_path=str(repo_path / "predict.py"),
                        requirements_path=str(repo_path / "requirements.txt"),
                        test_data_path=str(repo_path / "test_data.json"),
                        created_at=datetime.fromisoformat(model_data["created_at"]),
                        updated_at=datetime.fromisoformat(model_data["updated_at"])
                    )
                    
                    # Re-register the model API
                    await self._register_model_api(metadata, repo_path, main_app)
                    reloaded_count += 1
                    
                    logger.info(f"Successfully reloaded model: {model_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to reload model {model_id}: {e}")
                    failed_count += 1
            
            logger.info(f"Model reload completed: {reloaded_count} successful, {failed_count} failed")
            
            return {
                "reloaded_count": reloaded_count,
                "failed_count": failed_count,
                "total_attempted": len(registered_models),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to reload models from registry: {e}")
            return {
                "reloaded_count": 0,
                "failed_count": len(registered_models),
                "total_attempted": len(registered_models),
                "status": "failed",
                "error": str(e)
            } 