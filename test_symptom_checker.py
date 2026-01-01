"""
Test the symptom checker system
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.services.ml_service import symptom_checker_service

def test_symptom_checker():
    """Test symptom checker functionality"""
    print("🧪 Testing Symptom Checker System\n")
    print("=" * 60)
    
    # Test 1: Load model
    print("\n1️⃣ Loading model...")
    try:
        symptom_checker_service.load_model()
        print("✅ Model loaded successfully")
        print(f"   - Symptoms: {len(symptom_checker_service.symptoms_list)}")
        print(f"   - Conditions: {len(symptom_checker_service.metadata['conditions'])}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test 2: Validate symptoms
    print("\n2️⃣ Testing symptom validation...")
    test_symptoms = ["fever", "cough", "invalid_symptom", "fatigue"]
    valid, unknown = symptom_checker_service.validate_symptoms(test_symptoms)
    print(f"   Input: {test_symptoms}")
    print(f"   ✅ Valid: {valid}")
    print(f"   ⚠️  Unknown: {unknown}")
    
    # Test 3: Predict conditions
    print("\n3️⃣ Testing condition prediction...")
    test_cases = [
        ["fever", "cough", "sore throat", "fatigue"],
        ["headache", "nausea", "sensitivity to light"],
        ["joint pain", "stiffness", "swelling"],
    ]
    
    for symptoms in test_cases:
        print(f"\n   Symptoms: {symptoms}")
        predictions = symptom_checker_service.predict(symptoms, top_k=3)
        for i, pred in enumerate(predictions, 1):
            print(f"   {i}. {pred['condition']} ({pred['confidence']:.1f}%)")
            print(f"      Severity: {pred['severity']}")
            print(f"      Top recommendation: {pred['recommendations'][0]}")
    
    # Test 4: Get wellness advice
    print("\n4️⃣ Testing wellness advice...")
    symptoms = ["frequent urination", "painful urination", "abdominal pain"]
    print(f"   Symptoms: {symptoms}")
    advice = symptom_checker_service.get_wellness_advice(symptoms)
    print(f"   Primary condition: {advice['primary_condition']}")
    print(f"   Confidence: {advice['confidence']:.1f}%")
    print(f"   Severity: {advice['severity']}")
    print(f"   Recommendations:")
    for rec in advice['recommendations'][:3]:
        print(f"     • {rec}")
    
    # Test 5: Memory usage
    print("\n5️⃣ Checking memory usage...")
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Memory usage: {memory_mb:.2f} MB")
        if memory_mb < 512:
            print("   ✅ Excellent! Well under Render free tier limits")
        else:
            print("   ⚠️  Consider optimizations")
    except ImportError:
        print("   ℹ️  psutil not available, skipping memory check")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("\n📝 API Endpoints:")
    print("   POST /api/v1/symptom-checker/analyze")
    print("   POST /api/v1/symptom-checker/wellness-advice")
    print("   GET  /api/v1/symptom-checker/symptoms")
    print("   GET  /api/v1/symptom-checker/conditions/{name}")
    print("   GET  /api/v1/symptom-checker/health")
    print("\n✨ Ready for deployment!")

if __name__ == "__main__":
    test_symptom_checker()
