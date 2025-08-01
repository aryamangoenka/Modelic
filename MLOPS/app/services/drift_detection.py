"""
Drift Detection Service for MLOps Platform.

This service provides comprehensive drift detection capabilities using 
PSI (Population Stability Index) and KL divergence for monitoring
model performance and data distribution changes.
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.utils.statistics import (
    create_histogram_bins,
    normalize_distribution,
    calculate_categorical_distribution,
    align_categorical_distributions,
    validate_distribution_data,
    calculate_bin_statistics
)
from app.db.database import (
    get_baseline_stats,
    get_inference_logs
)

logger = logging.getLogger(__name__)


class DriftSeverity(str, Enum):
    """Drift severity levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class DriftResult:
    """Result of drift detection for a single feature."""
    feature_name: str
    feature_type: str  # "numerical" or "categorical"
    drift_score: float
    threshold: float
    drift_detected: bool
    severity: DriftSeverity
    baseline_samples: int
    current_samples: int
    additional_metrics: Dict[str, Any]


@dataclass
class ModelDriftReport:
    """Complete drift report for a model."""
    model_id: str
    timestamp: datetime
    overall_drift_detected: bool
    overall_severity: DriftSeverity
    feature_drift_results: List[DriftResult]
    summary_statistics: Dict[str, Any]
    baseline_period: str
    current_period: str


class DriftDetectionService:
    """Service for detecting data drift in ML models."""
    
    def __init__(
        self,
        psi_threshold: float = 0.2,
        kl_divergence_threshold: float = 0.1,
        min_samples: int = 30
    ):
        """
        Initialize drift detection service.
        
        Args:
            psi_threshold: PSI threshold for significant drift
            kl_divergence_threshold: KL divergence threshold for significant drift
            min_samples: Minimum samples required for drift detection
        """
        self.psi_threshold = psi_threshold
        self.kl_divergence_threshold = kl_divergence_threshold
        self.min_samples = min_samples
        logger.info(f"Initialized DriftDetectionService with PSI threshold: {psi_threshold}, KL threshold: {kl_divergence_threshold}")

    def calculate_psi(
        self, 
        expected_dist: Dict[str, float], 
        actual_dist: Dict[str, float]
    ) -> float:
        """
        Calculate Population Stability Index (PSI) for categorical features.
        
        PSI = Σ[(actual% - expected%) * ln(actual% / expected%)]
        
        Args:
            expected_dist: Expected (baseline) distribution
            actual_dist: Actual (current) distribution
            
        Returns:
            PSI score (0 = no drift, >0.2 = significant drift)
        """
        try:
            # Align distributions to have same categories
            aligned_expected, aligned_actual = align_categorical_distributions(
                expected_dist, actual_dist
            )
            
            psi_score = 0.0
            
            for category in aligned_expected.keys():
                expected_pct = aligned_expected[category]
                actual_pct = aligned_actual[category]
                
                # Add small epsilon to avoid division by zero
                expected_pct = max(expected_pct, 1e-10)
                actual_pct = max(actual_pct, 1e-10)
                
                # PSI formula: (actual% - expected%) * ln(actual% / expected%)
                psi_component = (actual_pct - expected_pct) * np.log(actual_pct / expected_pct)
                psi_score += psi_component
            
            logger.debug(f"Calculated PSI: {psi_score:.4f} for {len(aligned_expected)} categories")
            return abs(psi_score)  # Take absolute value
            
        except Exception as e:
            logger.error(f"Error calculating PSI: {e}")
            raise ValueError(f"Failed to calculate PSI: {str(e)}")

    def calculate_kl_divergence(
        self, 
        p_distribution: np.ndarray, 
        q_distribution: np.ndarray
    ) -> float:
        """
        Calculate Kullback-Leibler divergence for numerical features.
        
        KL(P||Q) = Σ[P(i) * log(P(i) / Q(i))]
        
        Args:
            p_distribution: Reference (baseline) probability distribution
            q_distribution: Observed (current) probability distribution
            
        Returns:
            KL divergence score (0 = identical, higher = more different)
        """
        try:
            if len(p_distribution) != len(q_distribution):
                raise ValueError("Distributions must have the same length")
            
            # Normalize distributions and add smoothing
            p_norm = normalize_distribution(p_distribution, add_smoothing=True)
            q_norm = normalize_distribution(q_distribution, add_smoothing=True)
            
            # Calculate KL divergence
            # KL(P||Q) = Σ[P(i) * log(P(i) / Q(i))]
            kl_divergence = np.sum(p_norm * np.log(p_norm / q_norm))
            
            logger.debug(f"Calculated KL divergence: {kl_divergence:.4f}")
            return kl_divergence
            
        except Exception as e:
            logger.error(f"Error calculating KL divergence: {e}")
            raise ValueError(f"Failed to calculate KL divergence: {str(e)}")

    def detect_feature_drift(
        self, 
        feature_name: str,
        baseline_data: List[Any], 
        current_data: List[Any],
        feature_type: str
    ) -> DriftResult:
        """
        Detect drift for a single feature.
        
        Args:
            feature_name: Name of the feature
            baseline_data: Baseline (training) data for the feature
            current_data: Current (inference) data for the feature
            feature_type: "numerical" or "categorical"
            
        Returns:
            DriftResult object with drift detection results
        """
        try:
            # Validate inputs
            validate_distribution_data(baseline_data, feature_type)
            validate_distribution_data(current_data, feature_type)
            
            if len(baseline_data) < self.min_samples or len(current_data) < self.min_samples:
                logger.warning(f"Insufficient samples for {feature_name}: baseline={len(baseline_data)}, current={len(current_data)}")
                return DriftResult(
                    feature_name=feature_name,
                    feature_type=feature_type,
                    drift_score=0.0,
                    threshold=0.0,
                    drift_detected=False,
                    severity=DriftSeverity.NONE,
                    baseline_samples=len(baseline_data),
                    current_samples=len(current_data),
                    additional_metrics={"error": "insufficient_samples"}
                )
            
            if feature_type == "categorical":
                return self._detect_categorical_drift(
                    feature_name, baseline_data, current_data
                )
            elif feature_type == "numerical":
                return self._detect_numerical_drift(
                    feature_name, baseline_data, current_data
                )
            else:
                raise ValueError(f"Unknown feature type: {feature_type}")
                
        except Exception as e:
            logger.error(f"Error detecting drift for feature {feature_name}: {e}")
            return DriftResult(
                feature_name=feature_name,
                feature_type=feature_type,
                drift_score=0.0,
                threshold=0.0,
                drift_detected=False,
                severity=DriftSeverity.NONE,
                baseline_samples=len(baseline_data) if baseline_data else 0,
                current_samples=len(current_data) if current_data else 0,
                additional_metrics={"error": str(e)}
            )

    def _detect_categorical_drift(
        self,
        feature_name: str,
        baseline_data: List[str],
        current_data: List[str]
    ) -> DriftResult:
        """Detect drift for categorical features using PSI."""
        try:
            # Calculate distributions
            baseline_dist = calculate_categorical_distribution([str(x) for x in baseline_data])
            current_dist = calculate_categorical_distribution([str(x) for x in current_data])
            
            # Calculate PSI
            psi_score = self.calculate_psi(baseline_dist, current_dist)
            
            # Determine drift status and severity
            drift_detected = psi_score > self.psi_threshold
            severity = self._determine_psi_severity(psi_score)
            
            # Additional metrics
            additional_metrics = {
                "baseline_distribution": baseline_dist,
                "current_distribution": current_dist,
                "unique_baseline_categories": len(baseline_dist),
                "unique_current_categories": len(current_dist),
                "psi_components": self._calculate_psi_components(baseline_dist, current_dist)
            }
            
            logger.info(f"Categorical drift detection for {feature_name}: PSI={psi_score:.4f}, drift={drift_detected}")
            
            return DriftResult(
                feature_name=feature_name,
                feature_type="categorical",
                drift_score=psi_score,
                threshold=self.psi_threshold,
                drift_detected=drift_detected,
                severity=severity,
                baseline_samples=len(baseline_data),
                current_samples=len(current_data),
                additional_metrics=additional_metrics
            )
            
        except Exception as e:
            logger.error(f"Error in categorical drift detection: {e}")
            raise

    def _detect_numerical_drift(
        self,
        feature_name: str,
        baseline_data: List[float],
        current_data: List[float]
    ) -> DriftResult:
        """Detect drift for numerical features using KL divergence."""
        try:
            # Create histograms with same bins
            baseline_counts, bin_edges = create_histogram_bins(baseline_data, num_bins=10)
            
            # Use same bin edges for current data
            current_counts, _ = np.histogram(current_data, bins=bin_edges)
            
            # Calculate KL divergence
            kl_divergence = self.calculate_kl_divergence(baseline_counts, current_counts)
            
            # Determine drift status and severity
            drift_detected = kl_divergence > self.kl_divergence_threshold
            severity = self._determine_kl_severity(kl_divergence)
            
            # Calculate additional statistics
            bin_stats = calculate_bin_statistics(baseline_counts, current_counts)
            
            additional_metrics = {
                "kl_divergence": kl_divergence,
                "bin_statistics": bin_stats,
                "baseline_mean": float(np.mean(baseline_data)),
                "current_mean": float(np.mean(current_data)),
                "baseline_std": float(np.std(baseline_data)),
                "current_std": float(np.std(current_data)),
                "mean_shift": float(np.mean(current_data) - np.mean(baseline_data)),
                "bin_edges": bin_edges.tolist()
            }
            
            logger.info(f"Numerical drift detection for {feature_name}: KL={kl_divergence:.4f}, drift={drift_detected}")
            
            return DriftResult(
                feature_name=feature_name,
                feature_type="numerical",
                drift_score=kl_divergence,
                threshold=self.kl_divergence_threshold,
                drift_detected=drift_detected,
                severity=severity,
                baseline_samples=len(baseline_data),
                current_samples=len(current_data),
                additional_metrics=additional_metrics
            )
            
        except Exception as e:
            logger.error(f"Error in numerical drift detection: {e}")
            raise

    def _determine_psi_severity(self, psi_score: float) -> DriftSeverity:
        """Determine drift severity based on PSI score."""
        if psi_score < 0.1:
            return DriftSeverity.NONE
        elif psi_score < 0.2:
            return DriftSeverity.LOW
        elif psi_score < 0.5:
            return DriftSeverity.MODERATE
        else:
            return DriftSeverity.HIGH

    def _determine_kl_severity(self, kl_score: float) -> DriftSeverity:
        """Determine drift severity based on KL divergence score."""
        if kl_score < 0.05:
            return DriftSeverity.NONE
        elif kl_score < 0.1:
            return DriftSeverity.LOW
        elif kl_score < 0.3:
            return DriftSeverity.MODERATE
        else:
            return DriftSeverity.HIGH

    def _calculate_psi_components(
        self, 
        baseline_dist: Dict[str, float], 
        current_dist: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate PSI components for each category."""
        aligned_baseline, aligned_current = align_categorical_distributions(
            baseline_dist, current_dist
        )
        
        components = {}
        for category in aligned_baseline.keys():
            expected_pct = max(aligned_baseline[category], 1e-10)
            actual_pct = max(aligned_current[category], 1e-10)
            component = (actual_pct - expected_pct) * np.log(actual_pct / expected_pct)
            components[category] = float(component)
            
        return components

    async def detect_model_drift(
        self, 
        model_id: str, 
        time_window_hours: int = 24
    ) -> ModelDriftReport:
        """
        Detect drift for an entire model across all features.
        
        Args:
            model_id: Model ID to check for drift
            time_window_hours: Time window for current data (hours)
            
        Returns:
            Complete drift report for the model
        """
        try:
            logger.info(f"Starting drift detection for model {model_id} with {time_window_hours}h window")
            
            # Get baseline statistics
            baseline_stats = get_baseline_stats(model_id)
            if not baseline_stats:
                raise ValueError(f"No baseline statistics found for model {model_id}")
            
            # Get recent inference logs
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=time_window_hours)
            
            logs = get_inference_logs(model_id=model_id, limit=1000)
            
            # First try to get logs within the time window
            recent_logs = [
                log for log in logs 
                if datetime.fromisoformat(log.get("timestamp", "")) >= cutoff_time
                and log.get("status") == "success"
            ]
            
            # If we don't have enough recent logs, use all available logs
            if len(recent_logs) < self.min_samples:
                logger.warning(f"Insufficient recent samples ({len(recent_logs)}), using all available logs")
                recent_logs = [log for log in logs if log.get("status") == "success"]
                
                if len(recent_logs) < self.min_samples:
                    raise ValueError(f"Insufficient samples: {len(recent_logs)} < {self.min_samples}")
                else:
                    logger.info(f"Using {len(recent_logs)} total logs for drift detection")
            else:
                logger.info(f"Using {len(recent_logs)} recent logs within {time_window_hours}h window")
            
            # Extract features from logs
            current_features = self._extract_features_from_logs(recent_logs)
            baseline_features = self._extract_baseline_features(baseline_stats)
            
            # Detect drift for each feature
            feature_drift_results = []
            
            for feature_name in baseline_features.keys():
                if feature_name not in current_features:
                    logger.warning(f"Feature {feature_name} not found in current data")
                    continue
                
                baseline_data = baseline_features[feature_name]["data"]
                current_data = current_features[feature_name]["data"]
                feature_type = baseline_features[feature_name]["type"]
                
                drift_result = self.detect_feature_drift(
                    feature_name, baseline_data, current_data, feature_type
                )
                feature_drift_results.append(drift_result)
            
            # Determine overall drift status
            overall_drift_detected = any(result.drift_detected for result in feature_drift_results)
            overall_severity = self._determine_overall_severity(feature_drift_results)
            
            # Create summary statistics
            summary_stats = self._create_summary_statistics(feature_drift_results, recent_logs)
            
            # Determine the current period description
            if len(recent_logs) >= self.min_samples and any(
                datetime.fromisoformat(log.get("timestamp", "")) >= cutoff_time 
                for log in recent_logs
            ):
                current_period = f"last_{time_window_hours}h"
            else:
                current_period = "all_available_logs"
            
            report = ModelDriftReport(
                model_id=model_id,
                timestamp=current_time,
                overall_drift_detected=overall_drift_detected,
                overall_severity=overall_severity,
                feature_drift_results=feature_drift_results,
                summary_statistics=summary_stats,
                baseline_period="training_data",
                current_period=current_period
            )
            
            logger.info(f"Completed drift detection for model {model_id}: overall_drift={overall_drift_detected}, severity={overall_severity}")
            return report
            
        except Exception as e:
            logger.error(f"Error in model drift detection: {e}")
            raise ValueError(f"Failed to detect model drift: {str(e)}")

    def _extract_features_from_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract feature data from inference logs."""
        features = {}
        
        for log in logs:
            numerical_features = log.get("numerical_features", {})
            categorical_features = log.get("categorical_features", {})
            
            # Process numerical features
            for feature_name, value in numerical_features.items():
                if feature_name not in features:
                    features[feature_name] = {"data": [], "type": "numerical"}
                features[feature_name]["data"].append(value)
            
            # Process categorical features
            for feature_name, value in categorical_features.items():
                if feature_name not in features:
                    features[feature_name] = {"data": [], "type": "categorical"}
                features[feature_name]["data"].append(str(value))
        
        return features

    def _extract_baseline_features(self, baseline_stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract feature data from baseline statistics."""
        # This is a simplified implementation
        # In reality, you'd need to reconstruct or store raw baseline data
        # For now, we'll use synthetic data based on baseline statistics
        
        features = {}
        feature_stats = baseline_stats.get("feature_stats", {})
        
        for feature_name, stats in feature_stats.items():
            if feature_name.startswith("_"):
                continue
                
            if stats.get("type") == "numerical":
                # Generate synthetic baseline data based on statistics
                mean = stats.get("mean", 0)
                std = stats.get("std", 1)
                count = stats.get("count", 100)
                
                # Generate synthetic data (in production, you'd store actual baseline samples)
                synthetic_data = np.random.normal(mean, std, count).tolist()
                features[feature_name] = {"data": synthetic_data, "type": "numerical"}
                
            elif stats.get("type") == "categorical":
                # Generate synthetic categorical data
                value_dist = stats.get("value_distribution", {})
                count = stats.get("count", 100)
                
                synthetic_data = []
                for value, prob in value_dist.items():
                    num_samples = int(prob * count)
                    synthetic_data.extend([value] * num_samples)
                
                features[feature_name] = {"data": synthetic_data, "type": "categorical"}
        
        return features

    def _determine_overall_severity(self, feature_results: List[DriftResult]) -> DriftSeverity:
        """Determine overall drift severity from individual feature results."""
        if not feature_results:
            return DriftSeverity.NONE
        
        # Count drift detections by severity
        severity_counts = {severity: 0 for severity in DriftSeverity}
        for result in feature_results:
            severity_counts[result.severity] += 1
        
        # Determine overall severity
        if severity_counts[DriftSeverity.HIGH] > 0:
            return DriftSeverity.HIGH
        elif severity_counts[DriftSeverity.MODERATE] > 0:
            return DriftSeverity.MODERATE
        elif severity_counts[DriftSeverity.LOW] > 0:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE

    def _create_summary_statistics(
        self, 
        feature_results: List[DriftResult], 
        recent_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create summary statistics for the drift report."""
        return {
            "total_features_analyzed": len(feature_results),
            "features_with_drift": len([r for r in feature_results if r.drift_detected]),
            "drift_detection_rate": len([r for r in feature_results if r.drift_detected]) / len(feature_results) if feature_results else 0,
            "average_psi_score": np.mean([r.drift_score for r in feature_results if r.feature_type == "categorical"]) if any(r.feature_type == "categorical" for r in feature_results) else None,
            "average_kl_score": np.mean([r.drift_score for r in feature_results if r.feature_type == "numerical"]) if any(r.feature_type == "numerical" for r in feature_results) else None,
            "total_recent_samples": len(recent_logs),
            "psi_threshold": self.psi_threshold,
            "kl_threshold": self.kl_divergence_threshold
        } 