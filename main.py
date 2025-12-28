#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
os.chdir(current_dir)

print("=" * 50)
print("TELEMEDICINE BACKEND STARTUP")
print("=" * 50)
print(f"Working directory: {current_dir}")
print(f"Python version: {sys.version}")
print(f"PORT env var: {os.environ.get('PORT', 'Not set')}")

# Check if app directory exists
app_dir = current_dir / "app"
print(f"App directory exists: {app_dir.exists()}")

if app_dir.exists():
    app_files = list(app_dir.iterdir())
    print(f"App directory contents: {[f.name for f in app_files]}")

# Try to import and start the app
try:
    print("\n--- Attempting to import FastAPI app ---")
    
    # Import FastAPI app
    from app.main import app as fastapi_app
    print("✅ FastAPI app imported successfully")
    
    # Get configuration
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}")
    
    # Start server
    import uvicorn
    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\n--- Diagnostic Information ---")
    print("Current directory files:")
    for item in current_dir.iterdir():
        print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")
    
    if app_dir.exists():
        print("\nApp directory files:")
        for item in app_dir.iterdir():
            print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")
    
    print("\nPython sys.path:")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i}: {path}")
    
    # Try basic fallback
    try:
        print("\n--- Attempting fallback startup ---")
        os.system(f"cd {current_dir} && python -m uvicorn app.main:app --host 0.0.0.0 --port {os.environ.get('PORT', 8000)}")
    except Exception as fallback_error:
        print(f"❌ Fallback failed: {fallback_error}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Startup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)