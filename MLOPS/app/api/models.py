"""
Model management API endpoints
"""

import logging
import numpy as np
from fastapi import APIRouter, HTTPException, status
from typing import Optional, Any, Dict, List

from app.core.schemas import ModelListResponse
from app.services.model_service import ModelService
from app.db.database import get_inference_logs

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Models"])

# Service dependency
model_service = ModelService()


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to native Python types for JSON serialization.
    
    Args:
        obj: Object that may contain numpy types
        
    Returns:
        Object with numpy types converted to native Python types
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


@router.get("/", response_model=ModelListResponse)
async def list_models():
    """List all deployed models."""
    try:
        return model_service.list_models()
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to list models: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/logs")
async def get_inference_logs_endpoint(
    model_id: Optional[str] = None,
    limit: int = 50,
    status_filter: Optional[str] = None,
    latency_category: Optional[str] = None
):
    """
    Get inference logs for monitoring with enhanced filtering.
    
    Args:
        model_id: Optional model ID to filter by
        limit: Maximum number of logs (default 50, max 500)
        status_filter: Optional status filter ('success', 'error', etc.)
        latency_category: Optional latency filter ('fast', 'medium', 'slow', 'very_slow')
    """
    try:
        # Limit the maximum to prevent performance issues
        limit = min(limit, 500)  # Increased from 200 to 500
        
        logs = get_inference_logs(
            model_id=model_id,
            limit=limit,
            status_filter=status_filter
        )
        
        # Additional filtering by latency category
        if latency_category:
            logs = [log for log in logs if log.get("latency_category") == latency_category]
        
        # Calculate summary statistics
        if logs:
            total_requests = len(logs)
            successful_requests = len([log for log in logs if log.get("status") == "success"])
            error_requests = len([log for log in logs if log.get("status") == "error"])
            avg_latency = sum(log.get("latency_ms", 0) for log in logs) / total_requests
            latency_categories = {}
            for log in logs:
                cat = log.get("latency_category", "unknown")
                latency_categories[cat] = latency_categories.get(cat, 0) + 1
        else:
            total_requests = 0
            successful_requests = 0
            error_requests = 0
            avg_latency = 0
            latency_categories = {}
        
        return {
            "logs": logs,
            "total_returned": len(logs),
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_requests": error_requests,
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "error_rate": error_requests / total_requests if total_requests > 0 else 0,
                "average_latency_ms": avg_latency,
                "latency_distribution": latency_categories
            },
            "filters": {
                "model_id": model_id,
                "status_filter": status_filter,
                "latency_category": latency_category,
                "limit": limit
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get inference logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get inference logs: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/{model_id}/baseline")
async def get_model_baseline_stats(model_id: str):
    """
    Get baseline statistics for a specific model.
    
    Args:
        model_id: Model ID
        
    Returns:
        Baseline statistics for drift detection
    """
    try:
        from app.db.database import get_baseline_stats
        
        baseline_stats = get_baseline_stats(model_id)
        
        if not baseline_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"No baseline statistics found for model {model_id}", "trace": None}
            )
        
        return {
            "model_id": model_id,
            "baseline_stats": baseline_stats,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get baseline stats for model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get baseline statistics: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/{model_id}/monitoring")
async def get_model_monitoring_data(
    model_id: str,
    hours: int = 24,
    include_baseline: bool = True
):
    """
    Get comprehensive monitoring data for a specific model.
    
    Args:
        model_id: Model ID
        hours: Number of hours to look back (default 24)
        include_baseline: Whether to include baseline statistics
        
    Returns:
        Comprehensive monitoring data including logs, baseline, and analysis
    """
    try:
        from app.db.database import get_baseline_stats, get_inference_logs
        from datetime import datetime, timedelta
        
        # Get recent inference logs
        logs = get_inference_logs(model_id=model_id, limit=1000)
        
        # Filter by time window
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_logs = []
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log.get("timestamp", ""))
                if log_time >= cutoff_time:
                    recent_logs.append(log)
            except:
                # Include logs with invalid timestamps
                recent_logs.append(log)
        
        # Calculate monitoring metrics
        total_requests = len(recent_logs)
        if total_requests > 0:
            successful_requests = len([log for log in recent_logs if log.get("status") == "success"])
            error_requests = len([log for log in recent_logs if log.get("status") == "error"])
            
            latencies = [log.get("latency_ms", 0) for log in recent_logs]
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies) if latencies else 0
            min_latency = min(latencies) if latencies else 0
            
            # Feature analysis
            numerical_features = {}
            categorical_features = {}
            
            for log in recent_logs:
                if log.get("status") == "success" and log.get("numerical_features"):
                    for feature, value in log["numerical_features"].items():
                        if feature not in numerical_features:
                            numerical_features[feature] = []
                        numerical_features[feature].append(value)
                
                if log.get("status") == "success" and log.get("categorical_features"):
                    for feature, value in log["categorical_features"].items():
                        if feature not in categorical_features:
                            categorical_features[feature] = []
                        categorical_features[feature].append(value)
            
            # Calculate current statistics for comparison with baseline
            current_stats = {}
            for feature, values in numerical_features.items():
                if values:
                    import numpy as np
                    np_values = np.array(values)
                    current_stats[feature] = {
                        "count": len(values),
                        "mean": float(np.mean(np_values)),
                        "std": float(np.std(np_values)),
                        "min": float(np.min(np_values)),
                        "max": float(np.max(np_values))
                    }
        else:
            successful_requests = 0
            error_requests = 0
            avg_latency = 0
            max_latency = 0
            min_latency = 0
            current_stats = {}
        
        # Prepare response
        monitoring_data = {
            "model_id": model_id,
            "time_window_hours": hours,
            "metrics": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_requests": error_requests,
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "error_rate": error_requests / total_requests if total_requests > 0 else 0,
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "min_latency_ms": min_latency
            },
            "current_feature_stats": current_stats,
            "recent_logs_count": len(recent_logs),
            "status": "success"
        }
        
        # Include baseline statistics if requested
        if include_baseline:
            baseline_stats = get_baseline_stats(model_id)
            monitoring_data["baseline_stats"] = baseline_stats
        
        return monitoring_data
        
    except Exception as e:
        logger.error(f"Failed to get monitoring data for model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get monitoring data: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/{model_id}/info")
async def get_model_info(model_id: str):
    """Get information for a specific model."""
    try:
        model_info = model_service.get_model_info(model_id)
        
        if "error" in model_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": model_info["error"], "trace": None}
            )
        
        # Add additional endpoints information for compatibility
        model_info["endpoints"] = {
            "predict": f"/models/{model_id}/predict",
            "info": f"/models/{model_id}/info", 
            "health": f"/models/{model_id}/health",
            "baseline": f"/models/{model_id}/baseline",
            "monitoring": f"/models/{model_id}/monitoring",
            "drift": f"/models/{model_id}/drift",
            "drift/history": f"/models/{model_id}/drift/history"
        }
        
        return model_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info for {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get model info: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/{model_id}")
async def get_model_details(model_id: str):
    """Get details for a specific model (alias for /info endpoint)."""
    return await get_model_info(model_id)


# ============================================================================
# DRIFT DETECTION ENDPOINTS (Phase 2.2 Step 3)
# ============================================================================

@router.get("/{model_id}/drift")
async def get_model_drift_status(model_id: str):
    """
    Get current drift status for a specific model.
    
    Args:
        model_id: Model ID
        
    Returns:
        Current drift status and latest drift report
    """
    try:
        from app.db.database import get_latest_drift_status
        
        drift_status = get_latest_drift_status(model_id)
        
        if not drift_status:
            return {
                "model_id": model_id,
                "drift_status": "no_data",
                "message": "No drift detection data available for this model",
                "last_check": None,
                "overall_drift_detected": False,
                "overall_severity": "none",
                "feature_drift_count": 0,
                "status": "success"
            }
        
        # Calculate feature drift summary
        feature_drift_results = drift_status.get("feature_drift_results", [])
        drifted_features = [f for f in feature_drift_results if f.get("drift_detected", False)]
        
        # Convert numpy types to native Python types for JSON serialization
        sanitized_drift_status = convert_numpy_types(drift_status)
        
        return {
            "model_id": model_id,
            "drift_status": "available",
            "last_check": sanitized_drift_status.get("timestamp"),
            "overall_drift_detected": sanitized_drift_status.get("overall_drift_detected", False),
            "overall_severity": sanitized_drift_status.get("overall_severity", "none"),
            "feature_drift_count": len(drifted_features),
            "total_features_checked": len(feature_drift_results),
            "drift_summary": {
                "high_severity": len([f for f in drifted_features if f.get("severity") == "high"]),
                "moderate_severity": len([f for f in drifted_features if f.get("severity") == "moderate"]),
                "low_severity": len([f for f in drifted_features if f.get("severity") == "low"])
            },
            "latest_report": sanitized_drift_status,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get drift status for model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get drift status: {str(e)}", "trace": type(e).__name__}
        )


@router.get("/{model_id}/drift/history")
async def get_model_drift_history(
    model_id: str,
    days: int = 30,
    limit: int = 50
):
    """
    Get drift detection history for a specific model.
    
    Args:
        model_id: Model ID
        days: Number of days to look back (default 30)
        limit: Maximum number of reports to return (default 50)
        
    Returns:
        Historical drift reports and trends
    """
    try:
        from app.db.database import get_drift_history, get_all_feature_drift_trends
        
        # Get drift history
        drift_history = get_drift_history(
            model_id=model_id,
            days=days,
            limit=limit
        )
        
        # Get feature drift trends
        feature_trends = get_all_feature_drift_trends(
            model_id=model_id,
            days=days
        )
        
        # Calculate summary statistics
        if drift_history:
            total_reports = len(drift_history)
            reports_with_drift = len([r for r in drift_history if r.get("overall_drift_detected", False)])
            avg_severity_scores = []
            
            for report in drift_history:
                feature_results = report.get("feature_drift_results", [])
                if feature_results:
                    avg_score = sum(f.get("drift_score", 0) for f in feature_results) / len(feature_results)
                    avg_severity_scores.append(avg_score)
            
            avg_severity = sum(avg_severity_scores) / len(avg_severity_scores) if avg_severity_scores else 0
        else:
            total_reports = 0
            reports_with_drift = 0
            avg_severity = 0
        
        # Convert numpy types to native Python types for JSON serialization
        sanitized_drift_history = convert_numpy_types(drift_history)
        sanitized_feature_trends = convert_numpy_types(feature_trends)
        
        return {
            "model_id": model_id,
            "time_window_days": days,
            "summary": {
                "total_reports": total_reports,
                "reports_with_drift": reports_with_drift,
                "drift_detection_rate": reports_with_drift / total_reports if total_reports > 0 else 0,
                "average_severity_score": avg_severity
            },
            "drift_history": sanitized_drift_history,
            "feature_trends": sanitized_feature_trends,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get drift history for model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get drift history: {str(e)}", "trace": type(e).__name__}
        )


@router.post("/{model_id}/drift/check")
async def run_manual_drift_check(
    model_id: str,
    time_window_hours: Optional[int] = None
):
    """
    Manually trigger a drift detection check for a specific model.
    
    Args:
        model_id: Model ID
        time_window_hours: Optional time window for analysis (default from config)
        
    Returns:
        Drift detection results
    """
    try:
        from app.services.scheduled_drift_service import scheduled_drift_service
        
        # Run manual drift check
        result = await scheduled_drift_service.run_manual_drift_check(
            model_id=model_id,
            time_window_hours=time_window_hours
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": result["error"], "trace": None}
            )
        
        # Convert numpy types to native Python types for JSON serialization
        sanitized_result = convert_numpy_types(result)
        
        return {
            "model_id": model_id,
            "check_triggered": True,
            "result": sanitized_result,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run manual drift check for model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to run drift check: {str(e)}", "trace": type(e).__name__}
        )


# ============================================================================
# GLOBAL DRIFT ENDPOINTS
# ============================================================================

@router.get("/drift/summary")
async def get_drift_summary():
    """
    Get a summary of drift detection status across all models.
    
    Returns:
        Overall drift detection summary and alerts
    """
    try:
        from app.services.scheduled_drift_service import scheduled_drift_service
        from app.db.database import get_drift_alerts
        
        # Get drift status summary
        summary = await scheduled_drift_service.get_drift_status_summary()
        
        # Get active alerts
        alerts = get_drift_alerts(severity_threshold="moderate", hours_lookback=24)
        
        # Convert numpy types to native Python types for JSON serialization
        sanitized_summary = convert_numpy_types(summary)
        sanitized_alerts = convert_numpy_types(alerts)
        
        return {
            "summary": sanitized_summary,
            "active_alerts": sanitized_alerts,
            "alert_count": len(alerts),
            "high_severity_alerts": len([a for a in alerts if a.get("severity") == "high"]),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get drift summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to get drift summary: {str(e)}", "trace": type(e).__name__}
        )


@router.post("/drift/check-all")
async def run_drift_check_all_models():
    """
    Manually trigger drift detection for all models.
    
    Returns:
        Summary of drift checks performed
    """
    try:
        from app.services.scheduled_drift_service import scheduled_drift_service
        
        # Run drift check for all models
        result = await scheduled_drift_service.force_drift_check_all_models()
        
        # Convert numpy types to native Python types for JSON serialization
        sanitized_result = convert_numpy_types(result)
        
        return {
            "check_triggered": True,
            "models_checked": sanitized_result.get("models_checked", 0),
            "successful_checks": sanitized_result.get("successful_checks", 0),
            "failed_checks": sanitized_result.get("failed_checks", 0),
            "results": sanitized_result,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to run drift check for all models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to run drift checks: {str(e)}", "trace": type(e).__name__}
        ) 