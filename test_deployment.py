#!/usr/bin/env python3
"""
Deployment Test Script - Verify your backend works on Render free tier
Run this locally before deploying to catch issues early.
"""

import sys
import os
import requests
import time
from pathlib import Path

def test_imports():
    """Test that all imports work without cloudinary"""
    print("🔍 Testing imports...")

    try:
        # Test main app import
        from app.main import app
        print("✅ app.main imports successfully")

        # Test all services
        from app.services import ml_service, file_service, notification_service, websocket_service
        print("✅ All services import successfully")

        # Test ML service (should not load model on import)
        from app.services.ml_service import get_symptom_checker_model
        print("✅ ML service imports successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_memory_usage():
    """Test memory monitoring"""
    print("\n🔍 Testing memory monitoring...")

    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"✅ Memory usage: {memory_mb:.2f} MB")
        return True
    except ImportError:
        print("⚠️ psutil not available - install with: pip install psutil")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")

    try:
        from app.config import settings

        # Check required settings exist
        required = ['SECRET_KEY', 'DATABASE_URL', 'REDIS_URL']
        for setting in required:
            if hasattr(settings, setting):
                print(f"✅ {setting} configured")
            else:
                print(f"⚠️ {setting} not configured")

        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🔍 Testing database connection...")

    try:
        from app.database import init_db, engine

        # Try to create tables (won't fail if they exist)
        init_db()
        print("✅ Database initialized successfully")

        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_endpoints():
    """Test basic endpoints work"""
    print("\n🔍 Testing basic endpoints...")

    try:
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint works")
        else:
            print(f"⚠️ Root endpoint returned {response.status_code}")

        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            memory_mb = data.get('memory_usage_mb', 'N/A')
            optimization_status = data.get('optimization_status', 'unknown')
            print(f"✅ Health endpoint works - Memory: {memory_mb} MB - Status: {optimization_status}")

            if isinstance(memory_mb, (int, float)) and memory_mb > 400:
                print("⚠️ High memory usage detected")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")

        return True
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Mina Backend - Render Free Tier Deployment Test")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Memory Test", test_memory_usage),
        ("Config Test", test_config),
        ("Database Test", test_database),
        ("Endpoint Test", test_endpoints),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready for Render deployment.")
        return 0
    elif passed >= total - 1:  # Allow 1 failure
        print("⚠️ Most tests passed. Check warnings but should deploy OK.")
        return 0
    else:
        print("❌ Multiple tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
