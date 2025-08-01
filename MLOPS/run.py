#!/usr/bin/env python3
"""
Development server runner for the MLOps Platform API
Updated for modular structure.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for app imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Run the development server with hot reload."""
    try:
        import uvicorn
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import settings from new structure
        from app.core.config import settings
        
        print(f"🚀 Starting MLOps Platform API on http://{settings.fastapi_host}:{settings.fastapi_port}")
        print(f"📚 API Documentation: http://{settings.fastapi_host}:{settings.fastapi_port}/docs")
        print(f"🔄 Hot reload: {'enabled' if settings.fastapi_reload else 'disabled'}")
        print(f"📁 Model storage: {settings.model_storage_path}")
        print(f"📂 Repo storage: {settings.repo_storage_path}")
        
        # Run the server using the new modular app
        uvicorn.run(
            "app.main:app",
            host=settings.fastapi_host,
            port=settings.fastapi_port,
            reload=settings.fastapi_reload,
            log_level=settings.log_level.lower(),
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Error: Missing dependency: {e}")
        print("   Install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()