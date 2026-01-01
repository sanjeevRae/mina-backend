#!/usr/bin/env python
"""
Quick setup script for symptom checker
Generates dataset and trains model
"""
import sys
from pathlib import Path

print("🚀 Setting up AI Symptom Checker...")
print("=" * 60)

# Step 1: Generate dataset
print("\n1️⃣ Generating symptom-condition dataset...")
try:
    from data.symptom_dataset import save_dataset
    Path("data").mkdir(exist_ok=True)
    save_dataset("data/symptom_condition_data.json")
except Exception as e:
    print(f"❌ Error generating dataset: {e}")
    sys.exit(1)

# Step 2: Train model
print("\n2️⃣ Training LightGBM model...")
try:
    from train_symptom_model import main
    main()
except Exception as e:
    print(f"❌ Error training model: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Setup complete! Symptom checker is ready.")
print("\n📋 Next steps:")
print("   1. Start server: python start_server.py")
print("   2. Test API: python test_symptom_checker.py")
print("   3. View docs: http://localhost:8000/docs")
