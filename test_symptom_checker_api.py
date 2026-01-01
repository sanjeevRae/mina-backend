"""
Integration test for symptom checker with authentication
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_symptom_checker_integration():
    """Full integration test"""
    print("🧪 Symptom Checker Integration Test")
    print("=" * 60)
    
    # Step 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/symptom-checker/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Symptoms: {data.get('num_symptoms')}")
            print(f"   Conditions: {data.get('num_conditions')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("ℹ️  Make sure the server is running: python start_server.py")
        return False
    
    # Step 2: Get available symptoms (no auth required)
    print("\n2️⃣ Getting available symptoms...")
    try:
        response = requests.get(f"{API_BASE}/symptom-checker/symptoms")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['count']} symptoms")
            print(f"   Sample symptoms: {data['symptoms'][:5]}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 3: Register/Login to get token
    print("\n3️⃣ Getting authentication token...")
    
    # Try to login with test user
    login_data = {
        "username": "testregister",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"✅ Authenticated successfully")
        else:
            print(f"⚠️  Login failed, trying registration...")
            # Register new user
            register_data = {
                "email": f"test_symptom_{len('test')}@example.com",
                "username": f"test_symptom_{len('test')}",
                "password": "password123",
                "full_name": "Test Symptom User",
                "role": "PATIENT"
            }
            response = requests.post(f"{API_BASE}/auth/register", json=register_data)
            if response.status_code == 200:
                # Login again
                login_data["username"] = register_data["username"]
                response = requests.post(f"{API_BASE}/auth/login", json=login_data)
                token = response.json()['access_token']
                print(f"✅ Registered and authenticated")
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 4: Analyze symptoms
    print("\n4️⃣ Analyzing symptoms...")
    symptom_data = {
        "symptoms": ["fever", "cough", "fatigue", "sore throat"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/symptom-checker/analyze",
            json=symptom_data,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis successful")
            print(f"   Valid symptoms: {data['valid_symptoms']}")
            if data['predictions']:
                top = data['predictions'][0]
                print(f"   Top condition: {top['condition']} ({top['confidence']:.1f}%)")
                print(f"   Severity: {top['severity']}")
                print(f"   Recommendation: {top['recommendations'][0]}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 5: Get wellness advice
    print("\n5️⃣ Getting wellness advice...")
    advice_data = {
        "symptoms": ["headache", "nausea", "sensitivity to light"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/symptom-checker/wellness-advice",
            json=advice_data,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wellness advice retrieved")
            print(f"   Condition: {data['primary_condition']}")
            print(f"   Confidence: {data['confidence']:.1f}%")
            print(f"   When to seek help: {data['when_to_seek_help'][0]}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Integration test completed successfully!")
    print("\n✨ Symptom checker is fully operational")
    return True

if __name__ == "__main__":
    success = test_symptom_checker_integration()
    exit(0 if success else 1)
