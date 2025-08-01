#!/usr/bin/env python3
"""
Script to regenerate test data and verify inference logs.
This will create fresh test data and show you how to see all 100 logs.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the path
import sys
sys.path.append(str(Path(__file__).parent))

from app.db.database import (
    store_baseline_stats,
    log_inference,
    calculate_feature_statistics,
    get_inference_logs,
    _inference_logs
)

async def regenerate_test_data():
    """Regenerate test data and show log counts."""
    print("🔄 Regenerating test data...")
    
    # Clear existing logs (for demonstration)
    global _inference_logs
    _inference_logs.clear()
    
    # Model 1: Example model with numerical features
    model_1_id = "model_1_example-model-test"
    
    # Create synthetic baseline data
    np.random.seed(42)  # For reproducible results
    n_samples = 1000
    
    # Generate baseline data as list of dictionaries
    baseline_data = []
    for i in range(n_samples):
        age = np.random.normal(35, 10)  # Age: mean=35, std=10
        income = np.random.normal(50000, 15000)  # Income: mean=50000, std=15000
        education = np.random.choice(['high_school', 'bachelor', 'master', 'phd'], p=[0.3, 0.4, 0.2, 0.1])
        
        baseline_data.append({
            'age': age,
            'income': income,
            'education': education
        })
    
    # Calculate baseline statistics
    feature_stats = calculate_feature_statistics(baseline_data)
    
    # Store baseline statistics
    await store_baseline_stats(model_1_id, feature_stats, "synthetic_baseline")
    print(f"✅ Created baseline data for {model_1_id}")
    
    # Model 2: My ML model with different features
    model_2_id = "model_2_my-ml-model"
    
    # Create different baseline data for model 2
    np.random.seed(123)  # Different seed for different distribution
    n_samples_2 = 800
    
    # Generate baseline data for model 2
    baseline_data_2 = []
    for i in range(n_samples_2):
        feature_1 = np.random.normal(0, 1)  # Standard normal
        feature_2 = np.random.normal(5, 2)  # Different distribution
        category = np.random.choice(['A', 'B', 'C'], p=[0.5, 0.3, 0.2])
        
        baseline_data_2.append({
            'feature_1': feature_1,
            'feature_2': feature_2,
            'category': category
        })
    
    # Calculate baseline statistics for model 2
    feature_stats_2 = calculate_feature_statistics(baseline_data_2)
    
    # Store baseline statistics for model 2
    await store_baseline_stats(model_2_id, feature_stats_2, "synthetic_baseline")
    print(f"✅ Created baseline data for {model_2_id}")

async def create_inference_logs():
    """Create inference logs for both models."""
    print("📊 Creating inference logs...")
    
    # Model 1: Create logs with some drift
    model_1_id = "model_1_example-model-test"
    
    # Generate recent inference data with slight drift
    np.random.seed(456)  # Different seed for current data
    n_logs = 50
    
    for i in range(n_logs):
        # Simulate some drift in age (older population)
        age = np.random.normal(40, 12)  # Slightly older mean
        income = np.random.normal(52000, 16000)  # Slightly higher income
        education = np.random.choice(['high_school', 'bachelor', 'master', 'phd'], p=[0.25, 0.45, 0.25, 0.05])
        
        input_data = {
            'age': age,
            'income': income,
            'education': education
        }
        
        # Simulate prediction
        prediction = {
            'prediction': np.random.choice([0, 1], p=[0.7, 0.3]),
            'confidence': np.random.uniform(0.6, 0.95),
            'model_version': 'v20250726_131530'
        }
        
        # Log inference
        await log_inference(
            model_id=model_1_id,
            input_data=input_data,
            prediction=prediction,
            latency_ms=np.random.randint(10, 100),
            status="success"
        )
    
    print(f"✅ Created {n_logs} inference logs for {model_1_id}")
    
    # Model 2: Create logs with more significant drift
    model_2_id = "model_2_my-ml-model"
    
    for i in range(n_logs):
        # Simulate more significant drift in feature distributions
        feature_1 = np.random.normal(2, 1.5)  # Shifted mean
        feature_2 = np.random.normal(3, 3)  # Different distribution
        category = np.random.choice(['A', 'B', 'C'], p=[0.3, 0.5, 0.2])  # Different proportions
        
        input_data = {
            'feature_1': feature_1,
            'feature_2': feature_2,
            'category': category
        }
        
        # Simulate prediction
        prediction = {
            'prediction': np.random.choice([0, 1], p=[0.6, 0.4]),
            'confidence': np.random.uniform(0.5, 0.9),
            'model_version': 'v20250726_131716'
        }
        
        # Log inference
        await log_inference(
            model_id=model_2_id,
            input_data=input_data,
            prediction=prediction,
            latency_ms=np.random.randint(15, 120),
            status="success"
        )
    
    print(f"✅ Created {n_logs} inference logs for {model_2_id}")

def show_log_counts():
    """Show the current log counts for each model."""
    print("\n📈 Current Inference Log Counts:")
    print("=" * 50)
    
    # Get all logs
    all_logs = get_inference_logs(limit=1000)
    
    # Count by model
    model_counts = {}
    for log in all_logs:
        model_id = log.get("model_id", "unknown")
        model_counts[model_id] = model_counts.get(model_id, 0) + 1
    
    total_logs = len(all_logs)
    print(f"Total logs in system: {total_logs}")
    print()
    
    for model_id, count in model_counts.items():
        print(f"📊 {model_id}: {count} logs")
    
    print("\n🔍 To see all logs in the monitoring dashboard:")
    print("1. Go to http://localhost:3000/monitoring")
    print("2. Increase the 'Limit' filter to 200 or 500")
    print("3. Use the 'Refresh' button to reload data")
    print("4. You should now see all 100 logs (50 + 50)")
    
    print("\n🎯 To see logs for a specific model:")
    print("1. Go to a model's detail page")
    print("2. Click on the 'Monitoring' tab")
    print("3. The dashboard will automatically filter by that model")
    print("4. You should see 50 logs for that specific model")

async def main():
    """Main function to regenerate test data and show counts."""
    print("🚀 Regenerating test data for drift detection demonstration...")
    
    try:
        # Regenerate baseline data
        await regenerate_test_data()
        
        # Create inference logs
        await create_inference_logs()
        
        # Show log counts
        show_log_counts()
        
        print("\n✅ Test data regeneration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error regenerating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 