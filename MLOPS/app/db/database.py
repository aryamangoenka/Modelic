"""
Database operations for MLOps Platform
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import os
import json

logger = logging.getLogger(__name__)


# Constants
MODEL_STORAGE_PATH = os.getenv("MODEL_STORAGE_PATH", "/tmp/mlops_models")
REGISTRY_FILE = os.path.join(MODEL_STORAGE_PATH, "registry.json")
INFERENCE_LOGS_FILE = os.path.join(MODEL_STORAGE_PATH, "inference_logs.json")

class ModelStatus(str, Enum):
    """Model deployment status."""
    VALIDATING = "validating"
    DEPLOYED = "deployed"
    FAILED = "failed"
    PENDING = "pending"


class ModelMetadata:
    """Model metadata class (placeholder for database model)."""
    
    def __init__(
        self,
        id: str,
        name: str,
        version: str,
        status: ModelStatus,
        github_repo: str,
        model_file_path: str,
        predict_file_path: str,
        requirements_path: str,
        test_data_path: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.version = version
        self.status = status
        self.github_repo = github_repo
        self.model_file_path = model_file_path
        self.predict_file_path = predict_file_path
        self.requirements_path = requirements_path
        self.test_data_path = test_data_path
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()


# Global in-memory storage (will be replaced with Supabase)
_models_db: Dict[str, ModelMetadata] = {}
# Global storage (in-memory with file persistence)
_inference_logs: List[Dict[str, Any]] = []
_drift_reports: List[Dict[str, Any]] = []
_baseline_stats: Dict[str, Dict[str, Any]] = {}  # model_id -> baseline statistics

# File paths for persistence
INFERENCE_LOGS_FILE = os.path.join(MODEL_STORAGE_PATH, "inference_logs.json")
DRIFT_REPORTS_FILE = os.path.join(MODEL_STORAGE_PATH, "drift_reports.json")
BASELINE_STATS_FILE = os.path.join(MODEL_STORAGE_PATH, "baseline_stats.json")
REGISTRY_FILE = os.path.join(MODEL_STORAGE_PATH, "registry.json")


def _ensure_logs_file_exists():
    """Ensure the inference logs file exists."""
    os.makedirs(MODEL_STORAGE_PATH, exist_ok=True)
    if not os.path.exists(INFERENCE_LOGS_FILE):
        with open(INFERENCE_LOGS_FILE, "w") as f:
            json.dump({"logs": []}, f)


def _load_inference_logs_from_file():
    """Load inference logs from file into memory."""
    global _inference_logs
    try:
        _ensure_logs_file_exists()
        with open(INFERENCE_LOGS_FILE, "r") as f:
            data = json.load(f)
            _inference_logs = data.get("logs", [])
            logger.info(f"Loaded {len(_inference_logs)} inference logs from file")
    except Exception as e:
        logger.error(f"Failed to load inference logs from file: {e}")
        _inference_logs = []


def _save_inference_logs_to_file():
    """Save inference logs from memory to file."""
    try:
        _ensure_logs_file_exists()
        with open(INFERENCE_LOGS_FILE, "w") as f:
            json.dump({"logs": _inference_logs}, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save inference logs to file: {e}")


def _ensure_drift_reports_file_exists():
    """Ensure the drift reports file exists."""
    os.makedirs(MODEL_STORAGE_PATH, exist_ok=True)
    if not os.path.exists(DRIFT_REPORTS_FILE):
        with open(DRIFT_REPORTS_FILE, "w") as f:
            json.dump({"reports": []}, f)


def _save_drift_reports_to_file():
    """Save drift reports to file for persistence."""
    try:
        _ensure_drift_reports_file_exists()
        with open(DRIFT_REPORTS_FILE, "w") as f:
            json.dump({"reports": _drift_reports}, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save drift reports to file: {e}")


def _ensure_baseline_stats_file_exists():
    """Ensure the baseline stats file exists."""
    os.makedirs(os.path.dirname(BASELINE_STATS_FILE), exist_ok=True)
    if not os.path.exists(BASELINE_STATS_FILE):
        with open(BASELINE_STATS_FILE, 'w') as f:
            json.dump({}, f)

def _load_baseline_stats_from_file():
    """Load baseline statistics from file."""
    global _baseline_stats
    try:
        _ensure_baseline_stats_file_exists()
        with open(BASELINE_STATS_FILE, 'r') as f:
            _baseline_stats = json.load(f)
        logger.info(f"Loaded {len(_baseline_stats)} baseline statistics from file")
    except Exception as e:
        logger.error(f"Failed to load baseline statistics: {e}")
        _baseline_stats = {}

def _save_baseline_stats_to_file():
    """Save baseline statistics to file."""
    try:
        _ensure_baseline_stats_file_exists()
        with open(BASELINE_STATS_FILE, 'w') as f:
            json.dump(_baseline_stats, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save baseline statistics to file: {e}")


def init_baseline_stats() -> int:
    """Initialize baseline statistics from file."""
    _load_baseline_stats_from_file()
    return len(_baseline_stats)


def init_supabase() -> bool:
    """Initialize Supabase connection (mock implementation)."""
    # Load existing inference logs from file
    _load_inference_logs_from_file()
    # Load existing drift reports from file
    init_drift_reports()
    # Load existing baseline stats from file
    init_baseline_stats()
    logger.info("Database initialization (mock mode)")
    return True


def init_inference_logs() -> int:
    """
    Initialize inference logs storage by loading from file.
    
    Returns:
        Number of logs loaded
    """
    _load_inference_logs_from_file()
    return len(_inference_logs)


async def create_model_record(
    name: str,
    github_repo: str,
    model_file_path: str,
    predict_file_path: str,
    requirements_path: str,
    test_data_path: str
) -> ModelMetadata:
    """
    Create a new model record in the database.
    
    Args:
        name: Model name
        github_repo: GitHub repository full name
        model_file_path: Path to model file
        predict_file_path: Path to predict.py
        requirements_path: Path to requirements.txt
        test_data_path: Path to test_data.json
        
    Returns:
        Created model metadata
    """
    # Generate unique ID (in production, use UUID or database auto-increment)
    model_id = f"model_{len(_models_db) + 1}_{name}"
    version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    metadata = ModelMetadata(
        id=model_id,
        name=name,
        version=version,
        status=ModelStatus.VALIDATING,
        github_repo=github_repo,
        model_file_path=model_file_path,
        predict_file_path=predict_file_path,
        requirements_path=requirements_path,
        test_data_path=test_data_path
    )
    
    _models_db[model_id] = metadata
    logger.info(f"Created model record: {model_id}")
    
    return metadata


async def update_model_status(model_id: str, status: ModelStatus) -> bool:
    """
    Update model status.
    
    Args:
        model_id: Model ID
        status: New status
        
    Returns:
        True if updated successfully
    """
    from app.models.registry import ModelRegistry
    
    success = False
    
    # Update in-memory database
    if model_id in _models_db:
        _models_db[model_id].status = status
        _models_db[model_id].updated_at = datetime.utcnow()
        logger.info(f"Updated model {model_id} status to {status} in database")
        success = True
    else:
        logger.error(f"Model {model_id} not found in database for status update")
    
    # Update registry file
    try:
        registry = ModelRegistry()
        registry_updated = registry.update_model_status(model_id, status.value)
        if registry_updated:
            logger.info(f"Updated model {model_id} status to {status} in registry")
        else:
            logger.error(f"Failed to update model {model_id} status in registry")
        success = success or registry_updated
    except Exception as e:
        logger.error(f"Error updating registry for model {model_id}: {e}")
    
    return success


async def create_deployment_record(
    model_id: str,
    endpoint_url: str,
    version: str
) -> Dict[str, Any]:
    """
    Create a deployment record.
    
    Args:
        model_id: Model ID
        endpoint_url: Deployment endpoint URL
        version: Model version
        
    Returns:
        Deployment record
    """
    deployment_record = {
        "id": f"deploy_{model_id}_{datetime.utcnow().timestamp()}",
        "model_id": model_id,
        "endpoint_url": endpoint_url,
        "version": version,
        "deployed_at": datetime.utcnow().isoformat(),
        "status": "deployed"
    }
    
    logger.info(f"Created deployment record for model {model_id}")
    return deployment_record


async def log_inference(
    model_id: str,
    input_data: Dict[str, Any],
    prediction: Dict[str, Any],
    latency_ms: int,
    status: str,
    error_message: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Log an inference request/response with enhanced monitoring data.
    
    Args:
        model_id: Model ID
        input_data: Input data for inference
        prediction: Prediction result
        latency_ms: Inference latency in milliseconds
        status: Inference status ('success', 'error', 'timeout')
        error_message: Error message if status is 'error'
        user_id: Optional user identifier for multi-tenant support
    """
    # Extract feature metadata for drift monitoring
    feature_count = len(input_data) if isinstance(input_data, dict) else 0
    feature_names = list(input_data.keys()) if isinstance(input_data, dict) else []
    
    # Enhanced feature analysis
    numerical_features = {}
    categorical_features = {}
    feature_types = {}
    
    if isinstance(input_data, dict):
        for feature_name, feature_value in input_data.items():
            feature_types[feature_name] = type(feature_value).__name__
            
            # Categorize features for drift detection
            if isinstance(feature_value, (int, float)):
                numerical_features[feature_name] = feature_value
            elif isinstance(feature_value, (str, bool)):
                categorical_features[feature_name] = str(feature_value)
    
    # Extract prediction metadata
    prediction_metadata = {}
    if isinstance(prediction, dict):
        prediction_metadata = {
            "prediction_type": type(prediction.get("prediction", prediction)).__name__,
            "has_confidence": "confidence" in prediction,
            "has_probabilities": "probabilities" in prediction or "proba" in prediction,
            "model_version": prediction.get("model_version"),
            "prediction_shape": len(prediction.get("prediction", [])) if isinstance(prediction.get("prediction"), list) else 1
        }
    
    inference_log = {
        "id": f"inference_{len(_inference_logs) + 1}",
        "model_id": model_id,
        "input_data": input_data,
        "prediction": prediction,
        "latency_ms": latency_ms,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        
        # Enhanced monitoring fields (Phase 2.1)
        "feature_count": feature_count,
        "feature_names": feature_names,
        "feature_types": feature_types,
        "numerical_features": numerical_features,
        "categorical_features": categorical_features,
        "prediction_metadata": prediction_metadata,
        
        # Error and user tracking
        "error_message": error_message,
        "user_id": user_id,
        
        # Additional metrics for monitoring
        "prediction_confidence": prediction.get("confidence") if isinstance(prediction, dict) else None,
        "model_version": prediction.get("model_version") if isinstance(prediction, dict) else None,
        "request_size_bytes": len(str(input_data).encode('utf-8')),
        "response_size_bytes": len(str(prediction).encode('utf-8')),
        
        # Performance categorization
        "latency_category": (
            "fast" if latency_ms < 100 else
            "medium" if latency_ms < 500 else
            "slow" if latency_ms < 2000 else
            "very_slow"
        )
    }
    
    _inference_logs.append(inference_log)
    logger.info(f"Logged inference for model {model_id} - status: {status}, latency: {latency_ms}ms, features: {feature_count}, category: {inference_log['latency_category']}")
    
    # Save logs to file for persistence
    _save_inference_logs_to_file()


def calculate_feature_statistics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for features from training/test data.
    
    Args:
        data: List of data samples (e.g., from test_data.json)
        
    Returns:
        Dictionary containing detailed feature statistics
    """
    if not data:
        return {}
    
    import numpy as np
    from collections import Counter
    
    # Initialize statistics containers
    feature_stats = {}
    
    # Get all feature names from the first sample
    if isinstance(data[0], dict):
        feature_names = set()
        for sample in data:
            if isinstance(sample, dict):
                feature_names.update(sample.keys())
        
        feature_names = list(feature_names)
    else:
        # Handle non-dict data (e.g., single values or lists)
        return {"_sample_count": len(data), "_data_type": "non_dict"}
    
    for feature_name in feature_names:
        # Extract values for this feature
        feature_values = []
        for sample in data:
            if isinstance(sample, dict) and feature_name in sample:
                feature_values.append(sample[feature_name])
        
        if not feature_values:
            continue
        
        # Determine feature type and calculate appropriate statistics
        sample_value = feature_values[0]
        
        if isinstance(sample_value, (int, float)):
            # Numerical feature statistics
            np_values = np.array([v for v in feature_values if isinstance(v, (int, float)) and not isinstance(v, bool)])
            
            if len(np_values) > 0:
                feature_stats[feature_name] = {
                    "type": "numerical",
                    "count": len(np_values),
                    "mean": float(np.mean(np_values)),
                    "std": float(np.std(np_values)),
                    "min": float(np.min(np_values)),
                    "max": float(np.max(np_values)),
                    "median": float(np.median(np_values)),
                    "percentiles": {
                        "25": float(np.percentile(np_values, 25)),
                        "75": float(np.percentile(np_values, 75)),
                        "90": float(np.percentile(np_values, 90)),
                        "95": float(np.percentile(np_values, 95))
                    },
                    "missing_count": len(feature_values) - len(np_values)
                }
                
                # Calculate histogram for distribution comparison
                hist, bin_edges = np.histogram(np_values, bins=10)
                feature_stats[feature_name]["histogram"] = {
                    "counts": hist.tolist(),
                    "bin_edges": bin_edges.tolist()
                }
        
        elif isinstance(sample_value, (str, bool)):
            # Categorical feature statistics
            str_values = [str(v) for v in feature_values if v is not None]
            value_counts = Counter(str_values)
            
            feature_stats[feature_name] = {
                "type": "categorical",
                "count": len(str_values),
                "unique_count": len(value_counts),
                "most_common": value_counts.most_common(10),  # Top 10 values
                "value_distribution": dict(value_counts),
                "missing_count": len(feature_values) - len(str_values)
            }
        
        else:
            # Other types (lists, objects, etc.)
            feature_stats[feature_name] = {
                "type": "complex",
                "count": len(feature_values),
                "sample_value": str(sample_value)[:100]  # First 100 chars as sample
            }
    
    # Add overall statistics
    feature_stats["_metadata"] = {
        "total_samples": len(data),
        "total_features": len(feature_names),
        "numerical_features": [name for name, stats in feature_stats.items() 
                              if isinstance(stats, dict) and stats.get("type") == "numerical"],
        "categorical_features": [name for name, stats in feature_stats.items() 
                               if isinstance(stats, dict) and stats.get("type") == "categorical"],
        "calculated_at": datetime.utcnow().isoformat()
    }
    
    return feature_stats


async def store_baseline_stats(
    model_id: str,
    feature_stats: Dict[str, Any],
    data_source: str = "test_data"
) -> None:
    """
    Store baseline statistics for a model (for drift detection).
    
    Args:
        model_id: Model ID
        feature_stats: Dictionary containing feature statistics
        data_source: Source of the data ('test_data', 'training_data', etc.)
    """
    baseline_record = {
        "model_id": model_id,
        "feature_stats": feature_stats,
        "data_source": data_source,
        "created_at": datetime.utcnow().isoformat(),
        "sample_count": feature_stats.get("_metadata", {}).get("total_samples", 0),
        "feature_count": feature_stats.get("_metadata", {}).get("total_features", 0),
        "numerical_feature_count": len(feature_stats.get("_metadata", {}).get("numerical_features", [])),
        "categorical_feature_count": len(feature_stats.get("_metadata", {}).get("categorical_features", []))
    }
    
    _baseline_stats[model_id] = baseline_record
    _save_baseline_stats_to_file()
    logger.info(f"Stored baseline statistics for model {model_id} from {data_source} - {baseline_record['sample_count']} samples, {baseline_record['feature_count']} features")


async def create_baseline_from_test_data(model_id: str, test_data_path: str) -> Dict[str, Any]:
    """
    Create baseline statistics from test_data.json file.
    
    Args:
        model_id: Model ID
        test_data_path: Path to test_data.json file
        
    Returns:
        Baseline statistics dictionary
    """
    try:
        import json
        
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        
        # Handle different test data formats
        if isinstance(test_data, list):
            # List of samples
            data_samples = test_data
        elif isinstance(test_data, dict):
            if "data" in test_data:
                # Wrapped in data key
                data_samples = test_data["data"]
            elif "samples" in test_data:
                # Wrapped in samples key
                data_samples = test_data["samples"]
            else:
                # Single sample
                data_samples = [test_data]
        else:
            # Single value
            data_samples = [{"value": test_data}]
        
        # Calculate feature statistics
        feature_stats = calculate_feature_statistics(data_samples)
        
        # Store baseline statistics
        await store_baseline_stats(
            model_id=model_id,
            feature_stats=feature_stats,
            data_source="test_data"
        )
        
        logger.info(f"Created baseline statistics for model {model_id} from {len(data_samples)} test samples")
        
        return feature_stats
        
    except Exception as e:
        logger.error(f"Failed to create baseline statistics for model {model_id}: {e}")
        raise Exception(f"Failed to create baseline statistics: {str(e)}")


def get_baseline_stats(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get baseline statistics for a model.
    
    Args:
        model_id: Model ID
        
    Returns:
        Baseline statistics or None if not found
    """
    return _baseline_stats.get(model_id)


def get_inference_logs(
    model_id: Optional[str] = None,
    limit: int = 100,
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get inference logs with optional filtering.
    
    Args:
        model_id: Optional model ID to filter by
        limit: Maximum number of logs to return (default 100, max 1000)
        status_filter: Optional status to filter by ('success', 'error', etc.)
        
    Returns:
        List of inference logs
    """
    # Safety: Load from file if memory is empty
    if not _inference_logs:
        _load_inference_logs_from_file()
    
    # Limit the maximum to prevent performance issues
    limit = min(limit, 1000)
    
    logs = _inference_logs.copy()
    
    # Apply filters
    if model_id:
        logs = [log for log in logs if log.get("model_id") == model_id]
    
    if status_filter:
        logs = [log for log in logs if log.get("status") == status_filter]
    
    # Sort by timestamp (most recent first) and limit
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs[:limit]


def get_model_by_id(model_id: str) -> Optional[ModelMetadata]:
    """Get model by ID."""
    return _models_db.get(model_id)


def get_all_models() -> Dict[str, ModelMetadata]:
    """Get all models."""
    return _models_db.copy()


# ============================================================================
# DRIFT DETECTION STORAGE (Phase 2.2 Step 2)
# ============================================================================

def init_drift_reports() -> int:
    """
    Initialize drift reports from file storage.
    
    Returns:
        Number of loaded drift reports
    """
    global _drift_reports
    try:
        _ensure_drift_reports_file_exists()
        with open(DRIFT_REPORTS_FILE, "r") as f:
            data = json.load(f)
            _drift_reports = data.get("reports", [])
        
        logger.info(f"Loaded {len(_drift_reports)} drift reports from storage")
        return len(_drift_reports)
    except Exception as e:
        logger.error(f"Failed to load drift reports: {e}")
        _drift_reports = []
        return 0


async def store_drift_report(drift_report: Dict[str, Any]) -> str:
    """
    Store a drift detection report.
    
    Args:
        drift_report: Complete drift report dictionary
        
    Returns:
        Report ID for the stored report
    """
    try:
        # Generate unique report ID
        report_id = f"drift_report_{len(_drift_reports) + 1}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Add metadata to the report
        enhanced_report = {
            "id": report_id,
            "created_at": datetime.utcnow().isoformat(),
            **drift_report
        }
        
        # Store in memory
        _drift_reports.append(enhanced_report)
        
        # Save to file
        _save_drift_reports_to_file()
        
        logger.info(f"Stored drift report {report_id} for model {drift_report.get('model_id')}")
        return report_id
        
    except Exception as e:
        logger.error(f"Failed to store drift report: {e}")
        raise Exception(f"Failed to store drift report: {str(e)}")


def get_drift_history(
    model_id: Optional[str] = None,
    days: int = 30,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get drift detection history.
    
    Args:
        model_id: Optional model ID to filter by
        days: Number of days to look back
        limit: Maximum number of reports to return
        
    Returns:
        List of drift reports
    """
    try:
        # Filter by time window
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        filtered_reports = []
        for report in _drift_reports:
            # Check time filter
            try:
                report_time = datetime.fromisoformat(report.get("created_at", ""))
                if report_time < cutoff_time:
                    continue
            except:
                # Include reports with invalid timestamps
                pass
            
            # Check model filter
            if model_id and report.get("model_id") != model_id:
                continue
            
            filtered_reports.append(report)
        
        # Sort by timestamp (newest first) and limit
        filtered_reports.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        
        return filtered_reports[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get drift history: {e}")
        return []


def get_latest_drift_status(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest drift status for a model.
    
    Args:
        model_id: Model ID
        
    Returns:
        Latest drift report or None if not found
    """
    try:
        model_reports = [
            report for report in _drift_reports 
            if report.get("model_id") == model_id
        ]
        
        if not model_reports:
            return None
        
        # Sort by timestamp and return the latest
        model_reports.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return model_reports[0]
        
    except Exception as e:
        logger.error(f"Failed to get latest drift status for model {model_id}: {e}")
        return None


def get_drift_summary_statistics(
    model_id: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get summary statistics for drift detection.
    
    Args:
        model_id: Optional model ID to filter by
        days: Number of days to analyze
        
    Returns:
        Summary statistics dictionary
    """
    try:
        reports = get_drift_history(model_id=model_id, days=days, limit=1000)
        
        if not reports:
            return {
                "total_reports": 0,
                "drift_detected_count": 0,
                "drift_detection_rate": 0.0,
                "average_features_analyzed": 0,
                "most_common_drift_severity": None,
                "models_with_drift": [],
                "analysis_period_days": days
            }
        
        # Calculate statistics
        total_reports = len(reports)
        drift_detected_count = len([r for r in reports if r.get("overall_drift_detected", False)])
        
        # Severity distribution
        severities = [r.get("overall_severity", "none") for r in reports]
        severity_counts = {}
        for severity in severities:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        most_common_severity = max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else None
        
        # Features analyzed
        features_analyzed = [
            len(r.get("feature_drift_results", [])) 
            for r in reports
        ]
        avg_features = sum(features_analyzed) / len(features_analyzed) if features_analyzed else 0
        
        # Models with drift
        models_with_drift = list(set([
            r.get("model_id") for r in reports 
            if r.get("overall_drift_detected", False)
        ]))
        
        return {
            "total_reports": total_reports,
            "drift_detected_count": drift_detected_count,
            "drift_detection_rate": drift_detected_count / total_reports if total_reports > 0 else 0.0,
            "average_features_analyzed": avg_features,
            "severity_distribution": severity_counts,
            "most_common_drift_severity": most_common_severity,
            "models_with_drift": models_with_drift,
            "analysis_period_days": days,
            "unique_models_analyzed": len(set([r.get("model_id") for r in reports]))
        }
        
    except Exception as e:
        logger.error(f"Failed to get drift summary statistics: {e}")
        return {"error": str(e)}


def get_feature_drift_trends(
    model_id: str,
    feature_name: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get drift trends for a specific feature over time.
    
    Args:
        model_id: Model ID
        feature_name: Feature name to analyze
        days: Number of days to analyze
        
    Returns:
        List of feature drift data points over time
    """
    try:
        reports = get_drift_history(model_id=model_id, days=days, limit=1000)
        
        feature_trends = []
        for report in reports:
            feature_results = report.get("feature_drift_results", [])
            
            for feature_result in feature_results:
                if feature_result.get("feature_name") == feature_name:
                    feature_trends.append({
                        "timestamp": report.get("created_at"),
                        "drift_score": feature_result.get("drift_score"),
                        "threshold": feature_result.get("threshold"),
                        "drift_detected": feature_result.get("drift_detected"),
                        "severity": feature_result.get("severity"),
                        "feature_type": feature_result.get("feature_type"),
                        "baseline_samples": feature_result.get("baseline_samples"),
                        "current_samples": feature_result.get("current_samples")
                    })
                    break
        
        # Sort by timestamp
        feature_trends.sort(key=lambda x: x.get("timestamp", ""))
        
        return feature_trends
        
    except Exception as e:
        logger.error(f"Failed to get feature drift trends: {e}")
        return []


def get_all_feature_drift_trends(
    model_id: str,
    days: int = 30
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get drift trends for all features of a model over time.
    
    Args:
        model_id: Model ID
        days: Number of days to analyze
        
    Returns:
        Dictionary mapping feature names to their drift trends
    """
    try:
        reports = get_drift_history(model_id=model_id, days=days, limit=1000)
        
        feature_trends = {}
        
        for report in reports:
            feature_results = report.get("feature_drift_results", [])
            
            for feature_result in feature_results:
                feature_name = feature_result.get("feature_name")
                if feature_name not in feature_trends:
                    feature_trends[feature_name] = []
                
                feature_trends[feature_name].append({
                    "timestamp": report.get("created_at"),
                    "drift_score": feature_result.get("drift_score"),
                    "threshold": feature_result.get("threshold"),
                    "drift_detected": feature_result.get("drift_detected"),
                    "severity": feature_result.get("severity"),
                    "feature_type": feature_result.get("feature_type"),
                    "baseline_samples": feature_result.get("baseline_samples"),
                    "current_samples": feature_result.get("current_samples")
                })
        
        # Sort each feature's trends by timestamp
        for feature_name in feature_trends:
            feature_trends[feature_name].sort(key=lambda x: x.get("timestamp", ""))
        
        return feature_trends
        
    except Exception as e:
        logger.error(f"Failed to get all feature drift trends: {e}")
        return {}


async def cleanup_old_drift_reports(days_to_keep: int = 90) -> int:
    """
    Clean up old drift reports to manage storage.
    
    Args:
        days_to_keep: Number of days of reports to keep
        
    Returns:
        Number of reports deleted
    """
    try:
        global _drift_reports
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        
        initial_count = len(_drift_reports)
        
        # Filter to keep only recent reports
        _drift_reports = [
            report for report in _drift_reports
            if datetime.fromisoformat(report.get("created_at", "")) >= cutoff_time
        ]
        
        deleted_count = initial_count - len(_drift_reports)
        
        # Save updated reports
        if deleted_count > 0:
            _save_drift_reports_to_file()
            logger.info(f"Cleaned up {deleted_count} old drift reports (keeping {days_to_keep} days)")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup drift reports: {e}")
        return 0


def get_models_requiring_drift_check(hours_since_last_check: int = 24) -> List[str]:
    """
    Get list of models that need drift detection checks.
    
    Args:
        hours_since_last_check: Hours since last drift check
        
    Returns:
        List of model IDs that need checking
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_since_last_check)
        
        # Get all unique model IDs from the database
        all_models = list(_models_db.keys())
        
        # Check which models have recent drift reports
        models_with_recent_checks = set()
        for report in _drift_reports:
            try:
                report_time = datetime.fromisoformat(report.get("created_at", ""))
                if report_time >= cutoff_time:
                    models_with_recent_checks.add(report.get("model_id"))
            except:
                continue
        
        # Return models that need checking
        models_needing_check = [
            model_id for model_id in all_models
            if model_id not in models_with_recent_checks
        ]
        
        logger.debug(f"Found {len(models_needing_check)} models requiring drift check")
        return models_needing_check
        
    except Exception as e:
        logger.error(f"Failed to get models requiring drift check: {e}")
        return []


async def store_drift_detection_config(
    model_id: str,
    config: Dict[str, Any]
) -> None:
    """
    Store drift detection configuration for a specific model.
    
    Args:
        model_id: Model ID
        config: Drift detection configuration
    """
    try:
        # This is a placeholder for future implementation
        # For now, we'll use global configuration
        logger.info(f"Drift detection config stored for model {model_id}: {config}")
        
    except Exception as e:
        logger.error(f"Failed to store drift detection config: {e}")
        raise


def get_drift_alerts(
    severity_threshold: str = "moderate",
    hours_lookback: int = 24
) -> List[Dict[str, Any]]:
    """
    Get active drift alerts that require attention.
    
    Args:
        severity_threshold: Minimum severity level ("low", "moderate", "high")
        hours_lookback: Hours to look back for alerts
        
    Returns:
        List of active drift alerts
    """
    try:
        severity_levels = {"low": 1, "moderate": 2, "high": 3}
        min_severity_level = severity_levels.get(severity_threshold.lower(), 2)
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)
        
        alerts = []
        for report in _drift_reports:
            try:
                # Check if report is recent
                report_time = datetime.fromisoformat(report.get("created_at", ""))
                if report_time < cutoff_time:
                    continue
                
                # Check if drift was detected
                if not report.get("overall_drift_detected", False):
                    continue
                
                # Check severity level
                report_severity = report.get("overall_severity", "none")
                if severity_levels.get(report_severity, 0) < min_severity_level:
                    continue
                
                # Create alert
                alert = {
                    "alert_id": f"drift_alert_{report.get('id')}",
                    "model_id": report.get("model_id"),
                    "severity": report_severity,
                    "drift_detected_at": report_time.isoformat(),
                    "features_with_drift": [
                        result.get("feature_name") for result in report.get("feature_drift_results", [])
                        if result.get("drift_detected", False)
                    ],
                    "summary_stats": report.get("summary_statistics", {}),
                    "report_id": report.get("id")
                }
                
                alerts.append(alert)
                
            except Exception as e:
                logger.warning(f"Error processing drift report for alerts: {e}")
                continue
        
        # Sort by severity and timestamp
        alerts.sort(
            key=lambda x: (
                severity_levels.get(x.get("severity", "none"), 0),
                x.get("drift_detected_at", "")
            ),
            reverse=True
        )
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get drift alerts: {e}")
        return [] 