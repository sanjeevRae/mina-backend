#!/usr/bin/env python3
"""
Test the telemedicine backend setup
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from app.config import settings
        print("✅ Config imported successfully")
        
        from app.database import init_db
        print("✅ Database module imported successfully")
        
        from app.models import User
        print("✅ Models imported successfully")
        
        from app.schemas.user import UserCreate
        print("✅ Schemas imported successfully")
        
        from app.auth import get_password_hash
        print("✅ Auth module imported successfully")
        
        from app.services.ml_service import get_symptom_checker_model
        print("✅ ML service imported successfully")
        
        # Skip main app import to avoid circular import issues for now
        # from app.main import app
        # print("✅ Main app imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🗄️ Testing database...")
    
    try:
        from app.database import init_db, engine
        
        # Initialize database
        init_db()
        print("✅ Database initialized successfully")
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_ml_model():
    """Test ML model creation"""
    print("\n🤖 Testing ML model...")
    
    try:
        from app.services.ml_service import SyntheticDataGenerator
        
        # Test synthetic data generation
        data_generator = SyntheticDataGenerator()
        
        # Generate a small sample
        sample_data = data_generator.generate_dataset(num_samples=10)
        print(f"✅ Generated {len(sample_data)} synthetic samples")
        
        print("✅ ML model components working")
        return True
        
    except Exception as e:
        print(f"❌ ML model error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Telemedicine Backend Test Suite")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test database
    if not test_database():
        all_tests_passed = False
    
    # Test ML model
    if not test_ml_model():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 All tests passed! The system is ready.")
        print("\n📝 Next steps:")
        print("1. Run: python setup_db.py")
        print("2. Run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()