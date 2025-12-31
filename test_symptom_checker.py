#!/usr/bin/env python3
"""
Test script for the symptom checker functionality
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.services.ml_service import get_symptom_checker_model, SymptomCheckerModel
from app.schemas.ml_models import SymptomInput, PatientInfo


def test_model_creation():
    """Test creating and initializing the model"""
    print("Testing model creation...")
    try:
        model = get_symptom_checker_model()
        print("[OK] Model created successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating model: {e}")
        return False


def test_training_with_sample_data():
    """Test training with sample data if symptom_data.csv doesn't exist"""
    print("\nTesting model training...")

    # Check if symptom_data.csv exists
    if not os.path.exists("data/symptom_data.csv"):
        print("[WARNING] data/symptom_data.csv not found. Creating sample data...")

        # Create sample data for testing
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

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Save sample data
        df = pd.DataFrame(sample_data)
        df.to_csv("data/symptom_data.csv", index=False)
        print("[OK] Sample data created at data/symptom_data.csv")

    try:
        model = SymptomCheckerModel()
        metrics = model.train(real_data_path="data/symptom_data.csv")
        print("[OK] Model trained successfully")
        print(f"Training metrics: {metrics}")

        # Save the model
        model_path = model.save_model()
        print(f"[OK] Model saved to: {model_path}")

        return True
    except Exception as e:
        print(f"[ERROR] Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction():
    """Test making predictions with the trained model"""
    print("\nTesting model prediction...")

    try:
        # Load the model
        model = get_symptom_checker_model()

        # If model is not trained, train it first
        if model.condition_classifier is None:
            print("Model not trained, training first...")
            model.train(real_data_path="data/symptom_data.csv")

        # Create sample symptoms
        symptoms = [
            SymptomInput(symptom="fever", severity=8),
            SymptomInput(symptom="cough", severity=6),
            SymptomInput(symptom="headache", severity=7)
        ]

        # Make prediction
        result = model.predict(symptoms=symptoms)

        print("[OK] Prediction successful")
        print(f"Predictions: {result['predictions']}")
        print(f"Urgency score: {result['urgency_score']}")
        print(f"Confidence score: {result['confidence_score']}")

        return True
    except Exception as e:
        print(f"[ERROR] Error making prediction: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Starting Symptom Checker Tests")
    print("="*50)

    tests = [
        ("Model Creation", test_model_creation),
        ("Model Training", test_training_with_sample_data),
        ("Model Prediction", test_prediction)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))

    print("\n" + "="*50)
    print("Test Results:")
    print("="*50)

    all_passed = True
    for test_name, success in results:
        status = "[OK] PASS" if success else "[ERROR] FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False

    print("="*50)
    if all_passed:
        print("[OK] All tests passed!")
        return 0
    else:
        print("[ERROR] Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())