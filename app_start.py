#!/usr/bin/env python3
"""Simple startup for Render deployment"""
import os
import sys
from pathlib import Path

# Ensure we're in the right directory
root = Path(__file__).parent.absolute()
os.chdir(root)
sys.path.insert(0, str(root))

try:
    from app.main import app
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
    
except Exception as e:
    print(f"Startup failed: {e}")
    sys.exit(1)