"""
GitHub service for repository operations
"""

import tempfile
import logging
from pathlib import Path
from typing import Tuple

import git

from app.core.exceptions import RepositoryError
from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for handling GitHub repository operations."""
    
    @staticmethod
    async def clone_repository(repo_url: str, repo_name: str) -> Path:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url: GitHub clone URL or local file path for testing
            repo_name: Repository name for logging
            
        Returns:
            Path to the cloned repository
            
        Raises:
            RepositoryError: If cloning fails
        """
        try:
            # Create temporary directory for cloned repos
            temp_dir = Path(settings.repo_storage_path)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique directory name
            clone_path = temp_dir / f"{repo_name}_{hash(repo_url) % 10000}"
            
            # Remove existing directory if it exists
            if clone_path.exists():
                import shutil
                shutil.rmtree(clone_path)
            
            # Handle local file URLs for testing
            if repo_url.startswith("file://"):
                local_path = Path(repo_url.replace("file://", ""))
                logger.info(f"Copying local repository {local_path} to {clone_path}")
                
                import shutil
                shutil.copytree(local_path, clone_path)
                
            else:
                # Clone repository
                logger.info(f"Cloning repository {repo_url} to {clone_path}")
                git.Repo.clone_from(repo_url, clone_path, depth=1)
            
            return clone_path
            
        except git.exc.GitCommandError as e:
            raise RepositoryError(f"Failed to clone repository: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error during cloning: {e}")
    
    @staticmethod
    def validate_webhook_payload(payload_data: dict) -> Tuple[bool, str]:
        """
        Validate GitHub webhook payload.
        
        Args:
            payload_data: Webhook payload data
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if it's a push to main/master branch
        ref = payload_data.get("ref", "")
        branch_name = ref.split('/')[-1] if ref else ""
        
        if branch_name not in ['main', 'master']:
            return False, f"Ignoring push to branch '{branch_name}'. Only main/master branches are processed."
        
        # Check required fields
        repository = payload_data.get("repository")
        if not repository:
            return False, "Missing repository information in webhook payload"
        
        required_repo_fields = ["name", "full_name", "clone_url"]
        for field in required_repo_fields:
            if field not in repository:
                return False, f"Missing required repository field: {field}"
        
        return True, "Valid webhook payload"
    
    @staticmethod
    def extract_repository_info(payload_data: dict) -> dict:
        """
        Extract repository information from webhook payload.
        
        Args:
            payload_data: Webhook payload data
            
        Returns:
            Repository information dictionary
        """
        repository = payload_data.get("repository", {})
        
        return {
            "repo_url": repository.get("clone_url"),
            "repo_name": repository.get("name"),
            "full_name": repository.get("full_name"),
            "branch": payload_data.get("ref", "").split('/')[-1]
        } 