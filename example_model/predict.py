import pickle
import numpy as np
from typing import Dict, Any
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent
model_path = script_dir / 'model.pkl'

# Load the model once when module is imported
with open(model_path, 'rb') as f:
    model = pickle.load(f)

def predict(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict using the trained logistic regression model.
    
    Args:
        input_data: Dictionary with features as values
        
    Returns:
        Dictionary with prediction and confidence
    """
    print("endjergn")
    try:
        # Extract features from input data
        features = [
            input_data.get("feature_1", 0.0),
            input_data.get("feature_2", 0.0), 
            input_data.get("feature_3", 0.0),
            input_data.get("feature_4", 0.0)
        ]
        
        # Convert to numpy array and reshape for single prediction
        X = np.array(features).reshape(1, -1)
        
        # Get prediction and probability
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        confidence = float(max(probabilities))
        
        return {
            "prediction": int(prediction),
            "confidence": confidence,
            "probabilities": {
                "class_0": float(probabilities[0]),
                "class_1": float(probabilities[1])
            }
        }
        
    except Exception as e:
        return {
            "prediction": None,
            "confidence": 0.0,
            "error": str(e)
        }
