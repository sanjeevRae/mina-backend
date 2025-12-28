#!/usr/bin/env python3
"""
Test script to verify app can be imported correctly
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all main imports work"""
    try:
        print("Testing core imports...")
        from app.config import settings
        print("✓ app.config imported successfully")
        
        from app.database import get_db, engine, Base
        print("✓ app.database imported successfully")
        
        from app.auth import create_access_token
        print("✓ app.auth imported successfully")
        
        from app.models.user import User
        print("✓ app.models.user imported successfully")
        
        from app.main import app
        print("✓ app.main imported successfully")
        
        print("\n✅ All imports successful! Your app should work on Render/Replit.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        print("This indicates there are still issues that need to be fixed.")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING APP STRUCTURE FOR RENDER/REPLIT")
    print("=" * 50)
    success = test_imports()
    sys.exit(0 if success else 1)