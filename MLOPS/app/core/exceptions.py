"""
Custom exceptions for MLOps Platform
"""


class RepositoryError(Exception):
    """Raised when repository operations fail."""
    pass


class ModelProcessingError(Exception):
    """Raised when model processing fails."""
    pass


class ModelValidationError(Exception):
    """Raised when model validation fails."""
    pass


class ModelDeploymentError(Exception):
    """Raised when model deployment fails."""
    pass 