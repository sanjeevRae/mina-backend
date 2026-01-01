#!/usr/bin/env python
"""
Quick setup script for symptom checker
Generates dataset and trains model
"""
import sys
import os
import subprocess
from pathlib import Path

print("🚀 Setting up AI Symptom Checker...")
print("=" * 60)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Step 1: Generate dataset
print("\n1️⃣ Generating symptom-condition dataset...")
try:
    # Run as subprocess for better isolation
    result = subprocess.run(
        [sys.executable, "data/symptom_dataset.py"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        print(f"❌ Dataset generation failed:")
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
except subprocess.TimeoutExpired:
    print("❌ Dataset generation timed out")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error generating dataset: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Train model
print("\n2️⃣ Training LightGBM model...")
try:
    result = subprocess.run(
        [sys.executable, "train_symptom_model.py"],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        print(f"❌ Model training failed:")
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
except subprocess.TimeoutExpired:
    print("❌ Model training timed out")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error training model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Setup complete! Symptom checker is ready.")
print("\n📋 Next steps:")
print("   1. Start server: python start_server.py")
print("   2. Test API: python test_symptom_checker.py")
print("   3. View docs: http://localhost:8000/docs")
