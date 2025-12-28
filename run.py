#!/usr/bin/env python3
"""
Render deployment startup script
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    # Get port from environment variable (Render sets PORT)
    port = int(os.environ.get("PORT", 8000))
    
    # Start the app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Never reload in production
        log_level="info"
    )