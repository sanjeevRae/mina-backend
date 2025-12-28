#!/usr/bin/env python3
"""
Render deployment startup script
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Also add the app directory to ensure it's found
app_dir = current_dir / "app"
if app_dir.exists():
    sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ.setdefault("PYTHONPATH", str(current_dir))

if __name__ == "__main__":
    try:
        import uvicorn
        from app.config import settings
        
        # Get port from environment variable (Render sets PORT)
        port = int(os.environ.get("PORT", 8000))
        
        print(f"Starting server on port {port}")
        print(f"Python path: {sys.path[:3]}...")
        print(f"Current directory: {current_dir}")
        print(f"App directory exists: {app_dir.exists()}")
        
        # Start the app
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Never reload in production
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)