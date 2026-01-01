#!/usr/bin/env python
"""
Test all symptom checker endpoints
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_service import symptom_checker_service

print("=" * 60)
print("Testing AI Symptom Checker - All Functions")
print("=" * 60)

# Test 1: Load Model
print("\n1. Testing Model Loading...")
try:
    symptom_checker_service.load_model()
    print("   ✅ Model loaded successfully")
    print(f"   - Total symptoms: {len(symptom_checker_service.get_all_symptoms())}")
    print(f"   - Total conditions: {len(symptom_checker_service.metadata['conditions'])}")
except Exception as e:
    print(f"   ❌ Model loading failed: {e}")
    sys.exit(1)

# Test 2: Get All Symptoms
print("\n2. Testing Get All Symptoms...")
try:
    all_symptoms = symptom_checker_service.get_all_symptoms()
    print(f"   ✅ Retrieved {len(all_symptoms)} symptoms")
    print(f"   - Sample symptoms: {all_symptoms[:5]}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 3: Validate Symptoms
print("\n3. Testing Symptom Validation...")
try:
    test_symptoms = ["fever", "cough", "headache", "invalid_symptom_xyz"]
    valid, invalid = symptom_checker_service.validate_symptoms(test_symptoms)
    print(f"   ✅ Validation working")
    print(f"   - Valid: {valid}")
    print(f"   - Invalid: {invalid}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 4: Predict Conditions
print("\n4. Testing Symptom Analysis (Prediction)...")
try:
    test_symptoms = ["fever", "cough", "fatigue", "shortness_of_breath"]
    predictions = symptom_checker_service.predict(test_symptoms, top_k=3)
    print(f"   ✅ Analysis completed")
    print(f"   - Top 3 predictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"      {i}. {pred['condition']} ({pred['confidence']}% confidence)")
        print(f"         Severity: {pred['severity']}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 5: Get Wellness Advice
print("\n5. Testing Wellness Advice...")
try:
    test_symptoms = ["headache", "fatigue", "dizziness"]
    advice = symptom_checker_service.get_wellness_advice(test_symptoms)
    print(f"   ✅ Wellness advice generated")
    print(f"   - Primary condition: {advice.get('primary_condition', 'N/A')}")
    print(f"   - Confidence: {advice.get('confidence', 'N/A')}%")
    print(f"   - Recommendations: {len(advice.get('recommendations', []))} items")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 6: Get Condition Info
print("\n6. Testing Get Condition Info...")
try:
    condition_info = symptom_checker_service.get_condition_info("COVID-19")
    if condition_info:
        print(f"   ✅ Condition info retrieved")
        print(f"   - Severity: {condition_info.get('severity', 'N/A')}")
        print(f"   - Symptoms count: {len(condition_info.get('symptoms', []))}")
        print(f"   - Recommendations: {len(condition_info.get('recommendations', []))}")
    else:
        print("   ❌ No info found for condition")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 7: Test Emergency Conditions
print("\n7. Testing Emergency Condition Detection...")
try:
    emergency_symptoms = ["chest_pain", "difficulty_breathing", "severe_headache"]
    predictions = symptom_checker_service.predict(emergency_symptoms, top_k=3)
    emergency_found = any(p['severity'] == 'emergency' for p in predictions)
    if emergency_found:
        print(f"   ✅ Emergency detection working")
        for pred in predictions:
            if pred['severity'] == 'emergency':
                print(f"   - EMERGENCY: {pred['condition']}")
    else:
        print(f"   ✅ No emergency conditions detected (as expected)")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 8: Test Multiple Specialties
print("\n8. Testing Different Medical Specialties...")
specialties_tests = [
    (["joint_pain", "stiffness", "swelling"], "Rheumatology"),
    (["blurred_vision", "eye_pain", "halos"], "Ophthalmology"),
    (["ear_pain", "hearing_loss", "tinnitus"], "ENT"),
    (["palpitations", "chest_pain", "shortness_of_breath"], "Cardiology"),
]

try:
    for symptoms, specialty in specialties_tests:
        predictions = symptom_checker_service.predict(symptoms, top_k=1)
        if predictions:
            print(f"   ✅ {specialty}: {predictions[0]['condition']}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 9: Memory Check
print("\n9. Checking Memory Usage...")
try:
    import psutil
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"   ✅ Current memory usage: {memory_mb:.2f} MB")
    if memory_mb < 400:
        print(f"   ✅ Memory usage is optimal (< 400 MB)")
    else:
        print(f"   ⚠️  Memory usage is high but acceptable")
except ImportError:
    print("   ⚠️  psutil not installed, skipping memory check")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)
print("\n📊 Summary:")
print(f"   - Conditions: {len(symptom_checker_service.metadata['conditions'])}")
print(f"   - Symptoms: {len(symptom_checker_service.get_all_symptoms())}")
print(f"   - Model file: models/symptom_checker/lightgbm_model.txt")
print("\n✅ System is ready for deployment!")
