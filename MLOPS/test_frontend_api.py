#!/usr/bin/env python3
"""
Test script to verify frontend API calls work through Next.js proxy.
This simulates the exact API calls the frontend makes.
"""

import requests
import json
from typing import Dict, Any

# Frontend API configuration (using Next.js proxy)
FRONTEND_API_BASE_URL = "http://localhost:3000/api"

def test_frontend_api_call(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test a frontend API call and return the response."""
    url = f"{FRONTEND_API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json()
            }
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"Request failed: {str(e)}"
        }

def main():
    """Test frontend API calls."""
    print("🧪 Testing Frontend API Calls (via Next.js Proxy)")
    print("=" * 60)
    
    # Test 1: Health endpoint
    print("\n1. Testing Health Endpoint (Frontend):")
    health_result = test_frontend_api_call("/health")
    print(f"   Status: {health_result['status']}")
    if health_result['status'] == 'success':
        print(f"   Models: {health_result['data'].get('registered_models', 'N/A')}")
    
    # Test 2: List models
    print("\n2. Testing List Models (Frontend):")
    models_result = test_frontend_api_call("/models/")
    print(f"   Status: {models_result['status']}")
    if models_result['status'] == 'success':
        models = models_result['data'].get('models', [])
        print(f"   Found {len(models)} models")
        for model in models:
            print(f"   - {model.get('model_id', 'N/A')}")
    
    # Test 3: Global drift summary
    print("\n3. Testing Global Drift Summary (Frontend):")
    drift_summary_result = test_frontend_api_call("/models/drift/summary")
    print(f"   Status: {drift_summary_result['status']}")
    if drift_summary_result['status'] == 'success':
        summary = drift_summary_result['data']
        print(f"   Active Alerts: {summary.get('alert_count', 0)}")
        print(f"   High Severity: {summary.get('high_severity_alerts', 0)}")
        print(f"   Scheduler Running: {summary.get('summary', {}).get('scheduler_running', False)}")
    
    # Test 4: Model-specific drift status
    print("\n4. Testing Model Drift Status (Frontend):")
    model_ids = ["model_1_example-model-test", "model_2_my-ml-model"]
    
    for model_id in model_ids:
        print(f"\n   Testing {model_id}:")
        drift_status_result = test_frontend_api_call(f"/models/{model_id}/drift")
        print(f"   Status: {drift_status_result['status']}")
        if drift_status_result['status'] == 'success':
            status_data = drift_status_result['data']
            print(f"   Drift Detected: {status_data.get('overall_drift_detected', False)}")
            print(f"   Severity: {status_data.get('overall_severity', 'N/A')}")
            print(f"   Features with Drift: {status_data.get('feature_drift_count', 0)}")
    
    # Test 5: Inference logs
    print("\n5. Testing Inference Logs (Frontend):")
    logs_result = test_frontend_api_call("/models/logs?limit=10")
    print(f"   Status: {logs_result['status']}")
    if logs_result['status'] == 'success':
        logs_data = logs_result['data']
        logs = logs_data.get('logs', [])
        print(f"   Logs: {len(logs)}")
        print(f"   Total Returned: {logs_data.get('total_returned', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ Frontend API Testing Complete!")
    
    # Summary
    print("\n📊 Summary:")
    if all([
        health_result['status'] == 'success',
        models_result['status'] == 'success',
        drift_summary_result['status'] == 'success'
    ]):
        print("✅ All frontend API calls are working correctly!")
        print("✅ Next.js proxy is functioning properly!")
        print("✅ Drift detection should work in the frontend!")
    else:
        print("❌ Some frontend API calls are failing!")
        print("❌ Check Next.js proxy configuration!")

if __name__ == "__main__":
    main() 