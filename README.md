# MLOps Platform - FastAPI Backend

A complete FastAPI backend for automated ML model deployment and monitoring. This platform provides a "Vercel for ML" experience - push your trained model to GitHub, and it automatically validates, deploys, and serves your model as an API.

## ✅ **Phase 1.1 Features (COMPLETED)**

✅ **GitHub Webhook Integration** - Automatic model deployment on push  
✅ **Model Validation** - Complete sklearn/PyTorch model loading and testing  
✅ **Dynamic API Generation** - Unique endpoints per model with `/predict`, `/info`, `/health`  
✅ **Database Integration** - Supabase for model metadata (with mock mode)  
✅ **Inference Logging** - Request/response logging for monitoring  
✅ **Model Management** - List, view, and manage deployed models

## ✅ **Phase 1.2 Features (COMPLETED)**

✅ **Dynamic FastAPI Route Creation** - Automatic endpoint generation per model  
✅ **Actual Model Loading & Validation** - Complete sklearn/PyTorch support  
✅ **Basic Inference Endpoints** - Working `/predict`, `/info`, `/health` endpoints

## ✅ **Phase 1.3 Features (COMPLETED)**

✅ **Frontend Integration** - Next.js frontend with real-time updates  
✅ **Model Dashboard** - List and status of all deployed models at http://localhost:3000  
✅ **Interactive Testing** - Built-in API testing interface for each model  
✅ **Deployment Monitoring** - Real-time status indicators and deployment tracking  
✅ **Documentation UI** - Interactive API documentation per model endpoint

### Frontend Components

```
frontend/
├── components/
│   ├── api-tester.tsx     # Interactive API testing interface
│   ├── model-card.tsx     # Individual model display
│   ├── model-list.tsx     # Models listing component
│   ├── status-indicator.tsx  # Deployment status display
│   └── layout/
│       ├── header.tsx     # Navigation header
│       └── layout.tsx     # Main layout wrapper
├── pages/
│   ├── index.tsx          # Dashboard home
│   └── models/            # Model-specific pages
└── styles/
    └── globals.css        # Global styles
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Access frontend
open http://localhost:3000
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Git
- Virtual environment (recommended)

### Installation

1. **Clone and setup environment:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your configuration
```

3. **Run the development server:**

```bash
# Direct run
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API:**

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎯 **Complete Phase 1.1 Usage**

### **Deploy a Model in 3 Steps**

**1. Create Model Repository:**

```bash
my-ml-model/
├── model.pkl              # Your trained sklearn model
├── predict.py             # Prediction function
├── requirements.txt       # Dependencies
└── test_data.json         # Sample input
```

**2. Send Webhook (or push to GitHub):**

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {
      "name": "my-model",
      "full_name": "user/my-model",
      "clone_url": "https://github.com/user/my-model.git"
    }
  }'
```

**3. Use Your Deployed Model:**

```bash
# Get model ID from webhook response
MODEL_ID="abc123-def456"

# Make predictions
curl -X POST http://localhost:8000/models/$MODEL_ID/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"feature_1": 1.0, "feature_2": -0.5}}'

# Response:
# {
#   "prediction": 1,
#   "confidence": 0.85,
#   "model_version": "v20240101_120000",
#   "inference_time_ms": 5,
#   "model_id": "abc123-def456"
# }
```

### **Example Working Model**

See `example_model/` directory for a complete working example with:

- ✅ Trained LogisticRegression model
- ✅ Proper predict.py implementation
- ✅ Valid test_data.json
- ✅ Requirements file

```bash
# Test with example model
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main","repository":{"name":"example-ml-model","full_name":"test/example-ml-model","clone_url":"file:///path/to/example_model"}}'
```

## 📋 API Endpoints

### Core Platform

- `GET /` - Platform welcome
- `GET /health` - System health check with registered model count
- `POST /webhook` - GitHub webhook handler (complete model deployment)

### Model Management ✅ **IMPLEMENTED**

- `GET /models` - List all deployed models
- `GET /models/{model_id}` - Get model details

### Dynamic Model APIs ✅ **IMPLEMENTED** (Created per model)

- `POST /models/{model_id}/predict` - Run inference with request/response logging
- `GET /models/{model_id}/info` - Model metadata and endpoint information
- `GET /models/{model_id}/health` - Model health check and readiness

## 🔗 GitHub Integration

### Webhook Setup

1. Go to your ML model repository on GitHub
2. Navigate to Settings → Webhooks
3. Add webhook with:
   - **Payload URL**: `https://your-domain.com/webhook`
   - **Content type**: `application/json`
   - **Events**: Push events
   - **Active**: ✅

### Required Repository Structure

Your ML model repository must contain:

```
ml-model-repo/
├── model.pkl              # Trained model (or .pt, .pth, .joblib)
├── requirements.txt       # Python dependencies
├── predict.py            # Inference function
└── test_data.json        # Sample input for validation
```

### Example `predict.py`:

```python
import joblib
import json
from typing import Dict, Any

# Load your model
model = joblib.load('model.pkl')

def predict(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main prediction function.

    Args:
        input_data: Dictionary with input features

    Returns:
        Dictionary with prediction and confidence
    """
    # Your prediction logic here
    prediction = model.predict([list(input_data.values())])[0]
    confidence = 0.95  # Calculate actual confidence

    return {
        "prediction": prediction,
        "confidence": confidence
    }
```

### Example `test_data.json`:

```json
{
  "feature1": 1.0,
  "feature2": 2.5,
  "feature3": "category_a"
}
```

## 🏗 Architecture

### Current Implementation (Phase 1.1)

- ✅ **FastAPI application** with auto-documentation
- ✅ **GitHub webhook handler** with payload validation
- ✅ **Repository cloning** and structure validation
- ✅ **Structured logging** with JSON output
- ✅ **Error handling** with custom exceptions
- ✅ **Type hints** and Pydantic models

### Coming Soon

- 🔄 **Model validation** with actual loading tests
- 🔄 **Dynamic API creation** for model inference
- 🔄 **Supabase integration** for metadata storage
- 🔄 **Celery background tasks** for async processing
- 🔄 **Drift detection** with PSI/KL divergence

## 🛠 Development

### Project Structure

```
mlops-platform/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── env.example         # Environment template
└── README.md           # This file
```

### Logging

The application uses structured logging with JSON output. Logs include:

- Request tracing with correlation IDs
- GitHub webhook processing details
- Repository cloning and validation results
- Error details with stack traces

### Testing the Webhook Locally

1. **Install ngrok** (for local testing):

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/
```

2. **Expose local server**:

```bash
# Run your FastAPI server
python main.py

# In another terminal, expose it
ngrok http 8000
```

3. **Use the ngrok URL** in your GitHub webhook configuration

### Example Webhook Payload Test

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {
      "id": 123456,
      "name": "my-ml-model",
      "full_name": "username/my-ml-model",
      "clone_url": "https://github.com/username/my-ml-model.git",
      "default_branch": "main"
    },
    "head_commit": {
      "id": "abc123",
      "message": "Update model",
      "author": {"name": "Developer", "email": "dev@example.com"},
      "modified": ["model.pkl"],
      "added": []
    }
  }'
```

## 📈 Next Steps

1. **Phase 1.3**: Frontend Integration

   - Model dashboard
   - API documentation
   - Basic monitoring

2. **Phase 2**: Drift Detection & Monitoring
   - Inference logging
   - PSI/KL divergence calculations
   - Alert system

## 🤝 Contributing

This project follows the architecture rules defined in `.cursor/rules`. Key principles:

- Use FastAPI as the only backend framework
- Always use type hints and Pydantic models
- Use structured logging (no print statements)
- Implement proper error handling
- Follow the defined repository structure conventions

## 📄 License

MIT License - see LICENSE file for details.
