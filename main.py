#!/usr/bin/env python3
"""
Alternative startup that sets up the environment properly
"""
import os
import sys
from pathlib import Path

# Get the directory this script is in
root_dir = Path(__file__).parent.absolute()

# Add it to Python path
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(root_dir)

# Change to the root directory
os.chdir(root_dir)

print(f"Root directory: {root_dir}")
print(f"Current working directory: {Path.cwd()}")
print(f"Python path includes: {sys.path[0]}")
print(f"App directory exists: {(root_dir / 'app').exists()}")

if __name__ == "__main__":
    try:
        # Import after setting up paths
        import uvicorn
        
        # Get port
        port = int(os.environ.get("PORT", 8000))
        
        print(f"Starting on port {port}")
        
        # Start uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"Import error: {e}")
        # Try importing the app directly to diagnose
        try:
            import app.main
            print("app.main imported successfully")
        except ImportError as e2:
            print(f"Could not import app.main: {e2}")
            print("Files in current directory:")
            print(list(Path('.').iterdir()))
            if Path('app').exists():
                print("Files in app directory:")
                print(list(Path('app').iterdir()))
        sys.exit(1)
    except Exception as e:
        print(f"Other error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)