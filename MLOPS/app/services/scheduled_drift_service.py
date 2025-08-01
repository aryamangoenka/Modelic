"""
Scheduled Drift Detection Service for MLOps Platform.

This service runs automated drift detection checks on deployed models
at configurable intervals and stores the results for monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.services.drift_detection import DriftDetectionService
from app.db.database import (
    store_drift_report,
    get_models_requiring_drift_check,
    get_latest_drift_status,
    cleanup_old_drift_reports
)

logger = logging.getLogger(__name__)


class ScheduledDriftService:
    """Service for running scheduled drift detection checks."""
    
    def __init__(self):
        """Initialize the scheduled drift service."""
        self.drift_detector = DriftDetectionService(
            psi_threshold=settings.drift_psi_threshold,
            kl_divergence_threshold=settings.drift_kl_divergence_threshold,
            min_samples=settings.drift_min_samples
        )
        self.is_running = False
        self._task = None
        logger.info("Initialized ScheduledDriftService")

    async def start_scheduler(self) -> None:
        """Start the drift detection scheduler."""
        if self.is_running:
            logger.warning("Drift detection scheduler is already running")
            return
        
        if not settings.drift_enable_auto_check:
            logger.info("Automated drift checking is disabled")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info(f"Started drift detection scheduler (interval: {settings.drift_check_interval_hours}h)")

    async def stop_scheduler(self) -> None:
        """Stop the drift detection scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped drift detection scheduler")

    async def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Run drift checks
                await self._run_scheduled_checks()
                
                # Cleanup old reports
                await self._cleanup_old_data()
                
                # Wait for next interval
                await asyncio.sleep(settings.drift_check_interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in drift detection scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def _run_scheduled_checks(self) -> None:
        """Run drift checks on models that need them."""
        try:
            # Get models that need drift checking
            models_to_check = get_models_requiring_drift_check(
                hours_since_last_check=settings.drift_check_interval_hours
            )
            
            if not models_to_check:
                logger.debug("No models require drift checking at this time")
                return
            
            logger.info(f"Running drift checks on {len(models_to_check)} models")
            
            # Run drift detection for each model
            successful_checks = 0
            failed_checks = 0
            
            for model_id in models_to_check:
                try:
                    await self._check_model_drift(model_id)
                    successful_checks += 1
                except Exception as e:
                    logger.error(f"Failed drift check for model {model_id}: {e}")
                    failed_checks += 1
            
            logger.info(f"Completed drift checks: {successful_checks} successful, {failed_checks} failed")
            
        except Exception as e:
            logger.error(f"Error running scheduled drift checks: {e}")

    async def _check_model_drift(self, model_id: str) -> Dict[str, Any]:
        """
        Run drift detection for a specific model.
        
        Args:
            model_id: Model ID to check
            
        Returns:
            Drift detection result summary
        """
        try:
            logger.debug(f"Starting drift check for model {model_id}")
            
            # Run drift detection
            drift_report = await self.drift_detector.detect_model_drift(
                model_id=model_id,
                time_window_hours=settings.drift_check_interval_hours
            )
            
            # Convert to dictionary for storage
            drift_report_dict = {
                "model_id": drift_report.model_id,
                "timestamp": drift_report.timestamp.isoformat(),
                "overall_drift_detected": drift_report.overall_drift_detected,
                "overall_severity": drift_report.overall_severity.value,
                "feature_drift_results": [
                    {
                        "feature_name": result.feature_name,
                        "feature_type": result.feature_type,
                        "drift_score": result.drift_score,
                        "threshold": result.threshold,
                        "drift_detected": result.drift_detected,
                        "severity": result.severity.value,
                        "baseline_samples": result.baseline_samples,
                        "current_samples": result.current_samples,
                        "additional_metrics": result.additional_metrics
                    }
                    for result in drift_report.feature_drift_results
                ],
                "summary_statistics": drift_report.summary_statistics,
                "baseline_period": drift_report.baseline_period,
                "current_period": drift_report.current_period
            }
            
            # Store the drift report
            report_id = await store_drift_report(drift_report_dict)
            
            logger.info(f"Stored drift report {report_id} for model {model_id}: "
                       f"drift_detected={drift_report.overall_drift_detected}, "
                       f"severity={drift_report.overall_severity}")
            
            return {
                "model_id": model_id,
                "report_id": report_id,
                "drift_detected": drift_report.overall_drift_detected,
                "severity": drift_report.overall_severity.value,
                "features_analyzed": len(drift_report.feature_drift_results),
                "timestamp": drift_report.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in drift check for model {model_id}: {e}")
            raise

    async def _cleanup_old_data(self) -> None:
        """Clean up old drift reports to manage storage."""
        try:
            deleted_count = await cleanup_old_drift_reports(days_to_keep=90)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old drift reports")
                
        except Exception as e:
            logger.error(f"Error cleaning up old drift reports: {e}")

    async def run_manual_drift_check(
        self, 
        model_id: str, 
        time_window_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run a manual drift check for a specific model.
        
        Args:
            model_id: Model ID to check
            time_window_hours: Optional time window override
            
        Returns:
            Drift check result
        """
        try:
            time_window = time_window_hours or settings.drift_check_interval_hours
            
            logger.info(f"Running manual drift check for model {model_id} (window: {time_window}h)")
            
            result = await self._check_model_drift(model_id)
            
            logger.info(f"Manual drift check completed for model {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"Manual drift check failed for model {model_id}: {e}")
            raise

    async def get_drift_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current drift detection status across all models.
        
        Returns:
            Summary of drift detection status
        """
        try:
            from app.db.database import get_drift_summary_statistics, get_drift_alerts
            
            # Get summary statistics
            summary_stats = get_drift_summary_statistics(days=7)
            
            # Get active alerts
            alerts = get_drift_alerts(severity_threshold="moderate", hours_lookback=24)
            
            # Get models requiring checks
            models_needing_check = get_models_requiring_drift_check(
                hours_since_last_check=settings.drift_check_interval_hours
            )
            
            return {
                "summary_statistics": summary_stats,
                "active_alerts": len(alerts),
                "high_severity_alerts": len([a for a in alerts if a.get("severity") == "high"]),
                "models_needing_check": len(models_needing_check),
                "scheduler_running": self.is_running,
                "check_interval_hours": settings.drift_check_interval_hours,
                "last_summary_generated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting drift status summary: {e}")
            return {"error": str(e)}

    async def force_drift_check_all_models(self) -> Dict[str, Any]:
        """
        Force drift detection on all deployed models (for testing/debugging).
        
        Returns:
            Summary of forced drift checks
        """
        try:
            from app.db.database import get_all_models
            
            all_models = get_all_models()
            model_ids = list(all_models.keys())
            
            if not model_ids:
                return {"message": "No models found for drift checking"}
            
            logger.info(f"Forcing drift checks on {len(model_ids)} models")
            
            results = []
            for model_id in model_ids:
                try:
                    result = await self._check_model_drift(model_id)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed forced drift check for {model_id}: {e}")
                    results.append({
                        "model_id": model_id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            successful = len([r for r in results if "error" not in r])
            failed = len([r for r in results if "error" in r])
            
            return {
                "total_models": len(model_ids),
                "successful_checks": successful,
                "failed_checks": failed,
                "results": results,
                "forced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error forcing drift checks: {e}")
            return {"error": str(e)}


# Global instance for the scheduled drift service
scheduled_drift_service = ScheduledDriftService() 