#!/usr/bin/env python3
"""
Direct FastAPI app startup for Render - bypasses module import issues
"""
import os
import sys
from pathlib import Path

# Get the directory this script is in
root_dir = Path(__file__).parent.absolute()

# Add it to Python path
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Set environment
os.environ['PYTHONPATH'] = str(root_dir)
os.chdir(root_dir)

print(f"Root directory: {root_dir}")
print(f"Current working directory: {Path.cwd()}")
print(f"App directory exists: {(root_dir / 'app').exists()}")

if __name__ == "__main__":
    try:
        # Import the FastAPI app directly
        sys.path.insert(0, str(root_dir))
        
        # Import app components
        from app.main import app
        
        print("✓ Successfully imported FastAPI app")
        
        # Get port
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"Starting server on {host}:{port}")
        
        # Start uvicorn with the app object directly (not module string)
        import uvicorn
        uvicorn.run(
            app,  # Pass the app object directly instead of module string
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Debugging file structure:")
        print(f"Current dir files: {list(Path('.').iterdir())}")
        if Path('app').exists():
            print(f"App dir files: {list(Path('app').iterdir())}")
            
        # Try alternative import methods
        try:
            import app
            print("✓ 'app' module exists")
            import app.main
            print("✓ 'app.main' module exists") 
            from app.main import app as fastapi_app
            print("✓ FastAPI app imported successfully")
            
            # If we get here, start the server
            port = int(os.environ.get("PORT", 8000))
            import uvicorn
            uvicorn.run(fastapi_app, host="0.0.0.0", port=port, reload=False, log_level="info")
            
        except Exception as e2:
            print(f"❌ Alternative import failed: {e2}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)