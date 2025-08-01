# Example ML Model

This is a simple logistic regression model for testing the MLOps platform.

## Model Details
- **Type**: Logistic Regression (sklearn)
- **Features**: 4 numerical features
- **Classes**: Binary classification (0 or 1)

## API Usage

### Prediction Request
```json
{
  "data": {
    "feature_1": 1.0,
    "feature_2": -0.5,
    "feature_3": 0.8,
    "feature_4": -1.2
  }
}
```

### Prediction Response
```json
{
  "prediction": 1,
  "confidence": 0.85,
  "model_version": "v20240101_120000",
  "inference_time_ms": 5,
  "model_id": "abc123-def456"
}
```

## Local Testing

```python
from predict import predict

test_input = {
    "feature_1": 1.0,
    "feature_2": -0.5, 
    "feature_3": 0.8,
    "feature_4": -1.2
}

result = predict(test_input)
print(result)
```
