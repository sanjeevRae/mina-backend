#!/usr/bin/env python3
"""
Direct startup without module imports - for Render
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Set port from environment
    port = int(os.environ.get("PORT", 8000))
    
    # Run uvicorn directly with the module path
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=port,
        reload=False,
        log_level="info"
    )