"""
Test script to verify the telemedicine backend is working
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Server is healthy!")
        return True
    return False

def test_authentication():
    """Test authentication flow"""
    print("\n🔐 Testing authentication...")
    
    # Test registration - should fail since users already exist
    register_data = {
        "email": "test@test.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "PATIENT"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    # Test login with existing user
    login_data = {
        "username": "admin@telemedicine.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Authentication working!")
        return token_data.get("access_token")
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_ml_symptom_checker(token):
    """Test ML symptom checker"""
    print("\n🤖 Testing ML symptom checker...")
    
    if not token:
        print("❌ No token available for ML test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start symptom checker session
    symptom_data = {
        "symptoms": ["headache", "fever", "fatigue"],
        "age": 30,
        "gender": "male"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/ml/symptom-checker/start", 
                           json=symptom_data, headers=headers)
    print(f"Symptom Checker Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ ML Analysis Complete!")
        print(f"Predictions: {len(result.get('predictions', []))} conditions")
        print(f"Urgency Score: {result.get('urgency_score', 'N/A')}")
        return True
    else:
        print(f"❌ ML test failed: {response.text}")
        return False

def test_medical_knowledge():
    """Test medical knowledge base"""
    print("\n🏥 Testing medical knowledge base...")
    
    # Test getting available conditions
    response = requests.get(f"{BASE_URL}/api/v1/ml/conditions")
    print(f"Knowledge Base Status: {response.status_code}")
    
    if response.status_code == 200:
        conditions = response.json()
        print(f"✅ Knowledge Base loaded with {len(conditions)} conditions")
        return True
    else:
        print(f"❌ Knowledge base test failed: {response.text}")
        return False

def test_file_upload(token):
    """Test file upload functionality"""
    print("\n📁 Testing file upload...")
    
    if not token:
        print("❌ No token available for upload test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test upload endpoint
    response = requests.get(f"{BASE_URL}/api/v1/files/upload-url", headers=headers)
    print(f"Upload URL Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ File upload system ready!")
        return True
    else:
        print(f"Upload test result: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🧪 Telemedicine Backend System Test")
    print("=" * 40)
    
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    
    # Test 2: Authentication
    token = test_authentication()
    results.append(token is not None)
    
    # Test 3: Medical Knowledge
    results.append(test_medical_knowledge())
    
    # Test 4: ML Symptom Checker
    results.append(test_ml_symptom_checker(token))
    
    # Test 5: File Upload
    results.append(test_file_upload(token))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully workable!")
        print("\n🌐 Access your API at:")
        print(f"   • API Docs: {BASE_URL}/docs")
        print(f"   • Health: {BASE_URL}/health")
        print(f"   • OpenAPI: {BASE_URL}/openapi.json")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the logs above.")
    
    print(f"\n📋 Login Credentials:")
    print("   • Admin: admin@telemedicine.com / admin123")
    print("   • Doctor: doctor@telemedicine.com / doctor123")
    print("   • Patient: patient@telemedicine.com / patient123")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")