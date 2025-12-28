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

print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Debug: List contents of project root and app folder
print("\n=== Directory Contents ===")
print(f"Project root contents: {os.listdir(project_root)}")

app_dir = os.path.join(project_root, "app")
if os.path.exists(app_dir):
    print(f"App folder exists: {app_dir}")
    print(f"App folder contents: {os.listdir(app_dir)}")
    
    models_dir = os.path.join(app_dir, "models")
    if os.path.exists(models_dir):
        print(f"Models folder exists: {models_dir}")
        print(f"Models folder contents: {os.listdir(models_dir)}")
    else:
        print(f"Models folder MISSING: {models_dir}")
else:
    print(f"App folder MISSING: {app_dir}")

print("=== End Directory Contents ===\n")

# Verify imports work
try:
    from app.main import app
    print("✓ App imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
