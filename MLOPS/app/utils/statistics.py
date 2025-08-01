"""
Statistical utilities for drift detection.

This module provides core statistical functions needed for calculating
PSI (Population Stability Index) and KL divergence for model drift detection.
"""

import logging
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


def create_histogram_bins(data: List[float], num_bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create histogram bins for numerical data.
    
    Args:
        data: List of numerical values
        num_bins: Number of bins to create
        
    Returns:
        Tuple of (bin_counts, bin_edges)
    """
    try:
        if not data:
            return np.array([]), np.array([])
        
        np_data = np.array(data)
        
        # Handle edge case where all values are the same
        if np.all(np_data == np_data[0]):
            # Create single bin for identical values
            bin_edges = np.array([np_data[0] - 0.5, np_data[0] + 0.5])
            bin_counts = np.array([len(data)])
            return bin_counts, bin_edges
        
        # Create histogram with specified number of bins
        bin_counts, bin_edges = np.histogram(np_data, bins=num_bins)
        
        logger.debug(f"Created {num_bins} bins for {len(data)} data points")
        return bin_counts, bin_edges
        
    except Exception as e:
        logger.error(f"Error creating histogram bins: {e}")
        raise ValueError(f"Failed to create histogram bins: {str(e)}")


def normalize_distribution(counts: np.ndarray, add_smoothing: bool = True) -> np.ndarray:
    """
    Normalize counts to create a probability distribution.
    
    Args:
        counts: Array of bin counts
        add_smoothing: Whether to add small epsilon to avoid zero probabilities
        
    Returns:
        Normalized probability distribution
    """
    try:
        if len(counts) == 0:
            return np.array([])
        
        # Add small smoothing value to avoid zero probabilities
        if add_smoothing:
            smoothed_counts = counts + 1e-10
        else:
            smoothed_counts = counts.copy()
        
        # Normalize to sum to 1
        total = np.sum(smoothed_counts)
        if total == 0:
            return np.ones_like(smoothed_counts) / len(smoothed_counts)
        
        probabilities = smoothed_counts / total
        
        logger.debug(f"Normalized distribution: sum={np.sum(probabilities):.6f}")
        return probabilities
        
    except Exception as e:
        logger.error(f"Error normalizing distribution: {e}")
        raise ValueError(f"Failed to normalize distribution: {str(e)}")


def calculate_categorical_distribution(data: List[str]) -> Dict[str, float]:
    """
    Calculate probability distribution for categorical data.
    
    Args:
        data: List of categorical values
        
    Returns:
        Dictionary mapping categories to their probabilities
    """
    try:
        if not data:
            return {}
        
        # Count occurrences of each category
        value_counts = Counter(data)
        total_count = len(data)
        
        # Convert to probabilities
        distribution = {
            category: count / total_count 
            for category, count in value_counts.items()
        }
        
        logger.debug(f"Categorical distribution: {len(distribution)} categories")
        return distribution
        
    except Exception as e:
        logger.error(f"Error calculating categorical distribution: {e}")
        raise ValueError(f"Failed to calculate categorical distribution: {str(e)}")


def align_categorical_distributions(
    baseline_dist: Dict[str, float], 
    current_dist: Dict[str, float]
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Align two categorical distributions to have the same categories.
    Missing categories are assigned zero probability.
    
    Args:
        baseline_dist: Baseline distribution
        current_dist: Current distribution
        
    Returns:
        Tuple of aligned (baseline_dist, current_dist)
    """
    try:
        # Get all unique categories from both distributions
        all_categories = set(baseline_dist.keys()) | set(current_dist.keys())
        
        # Align distributions
        aligned_baseline = {
            category: baseline_dist.get(category, 0.0) 
            for category in all_categories
        }
        aligned_current = {
            category: current_dist.get(category, 0.0) 
            for category in all_categories
        }
        
        logger.debug(f"Aligned distributions: {len(all_categories)} total categories")
        return aligned_baseline, aligned_current
        
    except Exception as e:
        logger.error(f"Error aligning categorical distributions: {e}")
        raise ValueError(f"Failed to align distributions: {str(e)}")


def calculate_distribution_similarity(
    dist1: np.ndarray, 
    dist2: np.ndarray, 
    method: str = "hellinger"
) -> float:
    """
    Calculate similarity between two probability distributions.
    
    Args:
        dist1: First probability distribution
        dist2: Second probability distribution
        method: Similarity method ("hellinger", "jensen_shannon")
        
    Returns:
        Similarity score (0 = identical, higher = more different)
    """
    try:
        if len(dist1) != len(dist2):
            raise ValueError("Distributions must have the same length")
        
        if method == "hellinger":
            # Hellinger distance
            sqrt_dist1 = np.sqrt(dist1)
            sqrt_dist2 = np.sqrt(dist2)
            hellinger_dist = np.sqrt(np.sum((sqrt_dist1 - sqrt_dist2) ** 2)) / np.sqrt(2)
            return hellinger_dist
            
        elif method == "jensen_shannon":
            # Jensen-Shannon divergence
            # Average of the two distributions
            m = 0.5 * (dist1 + dist2)
            
            # Calculate KL divergences (with smoothing to avoid log(0))
            kl1 = np.sum(dist1 * np.log((dist1 + 1e-10) / (m + 1e-10)))
            kl2 = np.sum(dist2 * np.log((dist2 + 1e-10) / (m + 1e-10)))
            
            js_divergence = 0.5 * kl1 + 0.5 * kl2
            return js_divergence
            
        else:
            raise ValueError(f"Unknown similarity method: {method}")
        
    except Exception as e:
        logger.error(f"Error calculating distribution similarity: {e}")
        raise ValueError(f"Failed to calculate similarity: {str(e)}")


def validate_distribution_data(
    data: List[Any], 
    data_type: str = "numerical"
) -> bool:
    """
    Validate data for distribution calculation.
    
    Args:
        data: Data to validate
        data_type: Type of data ("numerical" or "categorical")
        
    Returns:
        True if data is valid, raises ValueError if invalid
    """
    try:
        if not data:
            raise ValueError("Data cannot be empty")
        
        if data_type == "numerical":
            # Check if all values are numeric
            numeric_data = [x for x in data if isinstance(x, (int, float)) and not isinstance(x, bool)]
            if len(numeric_data) != len(data):
                raise ValueError("All values must be numeric for numerical distribution")
                
        elif data_type == "categorical":
            # Check if values are string-convertible
            try:
                [str(x) for x in data]
            except:
                raise ValueError("All values must be string-convertible for categorical distribution")
        
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        logger.debug(f"Validated {len(data)} {data_type} values")
        return True
        
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise


def calculate_bin_statistics(
    baseline_counts: np.ndarray, 
    current_counts: np.ndarray
) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics comparing two histograms.
    
    Args:
        baseline_counts: Baseline histogram counts
        current_counts: Current histogram counts
        
    Returns:
        Dictionary of comparison statistics
    """
    try:
        if len(baseline_counts) != len(current_counts):
            raise ValueError("Histogram counts must have the same length")
        
        # Normalize distributions
        baseline_prob = normalize_distribution(baseline_counts)
        current_prob = normalize_distribution(current_counts)
        
        # Calculate various metrics
        stats = {
            "total_baseline_samples": int(np.sum(baseline_counts)),
            "total_current_samples": int(np.sum(current_counts)),
            "num_bins": len(baseline_counts),
            "baseline_distribution": baseline_prob.tolist(),
            "current_distribution": current_prob.tolist(),
            "hellinger_distance": calculate_distribution_similarity(
                baseline_prob, current_prob, "hellinger"
            ),
            "jensen_shannon_divergence": calculate_distribution_similarity(
                baseline_prob, current_prob, "jensen_shannon"
            )
        }
        
        logger.debug(f"Calculated bin statistics for {stats['num_bins']} bins")
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating bin statistics: {e}")
        raise ValueError(f"Failed to calculate bin statistics: {str(e)}") 