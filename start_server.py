#!/usr/bin/env python
"""
Server startup script for Render deployment.
This script ensures the app package is discoverable before starting uvicorn.
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Verify imports work
try:
    from app.main import app
    print("✓ App imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {project_root}")
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
