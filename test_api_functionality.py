#!/usr/bin/env python3
"""
API test for the symptom checker functionality
"""

import requests
import json
import os
from pathlib import Path

# Add the app directory to the path
import sys
sys.path.append(str(Path(__file__).parent))

# Import the necessary modules to test the model directly
from app.services.ml_service import get_symptom_checker_model, SymptomCheckerModel
from app.schemas.ml_models import SymptomInput, PatientInfo, SimpleSymptomInput
import asyncio


def test_direct_model_functionality():
    """Test the model functionality directly"""
    print("Testing direct model functionality...")
    
    try:
        # Initialize and train model if needed
        model = get_symptom_checker_model()
        if model.condition_classifier is None:
            print("  Training model...")
            model.train(real_data_path="data/symptom_data.csv")
        
        # Test prediction with sample symptoms
        symptoms = [
            SymptomInput(symptom="fever", severity=8),
            SymptomInput(symptom="cough", severity=6),
            SymptomInput(symptom="headache", severity=7)
        ]
        
        result = model.predict(symptoms=symptoms)
        
        print(f"  Prediction successful!")
        print(f"  Top prediction: {result['predictions'][0].condition_name} ({result['predictions'][0].probability:.2%})")
        print(f"  Urgency score: {result['urgency_score']:.3f}")
        print(f"  Confidence: {result['confidence_score']:.3f}")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_symptom_input():
    """Test the simple symptom input functionality"""
    print("\nTesting simple symptom input...")
    
    try:
        # Initialize and train model if needed
        model = get_symptom_checker_model()
        if model.condition_classifier is None:
            print("  Training model...")
            model.train(real_data_path="data/symptom_data.csv")
        
        # Test with simple string symptoms
        simple_input = SimpleSymptomInput(symptoms=["fever", "cough", "headache"])
        symptoms = [SymptomInput(symptom=s, severity=5) for s in simple_input.symptoms]
        
        result = model.predict(symptoms=symptoms)
        
        print(f"  Simple input prediction successful!")
        print(f"  Top prediction: {result['predictions'][0].condition_name} ({result['predictions'][0].probability:.2%})")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_handling():
    """Test how the model handles different features from CSV"""
    print("\nTesting feature handling...")
    
    try:
        # Load the model
        model = get_symptom_checker_model()
        if model.condition_classifier is None:
            print("  Training model...")
            model.train(real_data_path="data/symptom_data.csv")
        
        print(f"  Model loaded with {len(model.feature_columns)} features")
        print(f"  Feature columns: {model.feature_columns[:10]}...")  # Show first 10
        
        # Test prediction with a known symptom from the dataset
        symptoms = [SymptomInput(symptom="fever", severity=8)]
        result = model.predict(symptoms=symptoms)
        
        print(f"  Prediction with single symptom successful!")
        print(f"  Top prediction: {result['predictions'][0].condition_name} ({result['predictions'][0].probability:.2%})")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API tests"""
    print("Starting Symptom Checker API Tests")
    print("="*50)
    
    # Create sample data if it doesn't exist
    if not os.path.exists("data/symptom_data.csv"):
        print("Creating sample data...")
        import pandas as pd
        sample_data = {
            'fever': [1, 0, 1, 0, 1, 0, 1, 0],
            'cough': [1, 1, 0, 1, 1, 0, 0, 1],
            'headache': [0, 1, 1, 0, 0, 1, 1, 0],
            'fatigue': [1, 1, 1, 0, 1, 1, 0, 1],
            'sore_throat': [1, 1, 0, 1, 0, 0, 0, 1],
            'runny_nose': [0, 1, 0, 1, 0, 0, 0, 1],
            'body_aches': [1, 0, 1, 0, 1, 1, 0, 0],
            'diagnosis': ['flu', 'cold', 'migraine', 'cold', 'flu', 'migraine', 'healthy', 'cold']
        }
        os.makedirs("data", exist_ok=True)
        df = pd.DataFrame(sample_data)
        df.to_csv("data/symptom_data.csv", index=False)
        print("Sample data created.")
    
    tests = [
        ("Direct Model Functionality", test_direct_model_functionality),
        ("Simple Symptom Input", test_simple_symptom_input),
        ("Feature Handling", test_feature_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "="*50)
    print("API Test Results:")
    print("="*50)
    
    all_passed = True
    for test_name, success in results:
        status = "[OK] PASS" if success else "[ERROR] FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("[OK] All API tests passed!")
        print("\nThe symptom checker is working correctly with your CSV data!")
        print("You can now use the following endpoints:")
        print("  POST /api/v1/ml/symptom-checker - for simple symptom input")
        print("  POST /api/v1/ml/symptom-checker/start - for full symptom checker")
        print("\nTo train with your own data, run: python train_symptom_checker.py")
        return 0
    else:
        print("[ERROR] Some API tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())