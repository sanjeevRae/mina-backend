#!/usr/bin/env python3
"""
Script to train the symptom checker model using symptom_data.csv
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.services.ml_service import SymptomCheckerModel
from app.database import SessionLocal
from app.models.ml_models import MLModel
from datetime import datetime


def train_model(data_path: str = "data/symptom_data.csv"):
    """Train the symptom checker model with CSV data"""
    print(f"Starting model training with data from: {data_path}")

    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return False

    # Initialize the model
    model = SymptomCheckerModel()

    try:
        # Train the model
        print("Training the model...")
        metrics = model.train(real_data_path=data_path)

        # Save the trained model
        print("Saving the trained model...")
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = model.save_model(version)

        # Update database with model info
        print("Updating model information in database...")
        db = SessionLocal()
        try:
            # Deactivate old models
            db.query(MLModel).filter(
                MLModel.model_name == "symptom_checker",
                MLModel.is_active == True
            ).update({"is_active": False})

            # Save new model info
            model_info = MLModel(
                model_name="symptom_checker",
                version=version,
                file_path=model_path,
                training_data_size=0,  # Will be calculated based on the dataset
                features_used=model.feature_columns,
                accuracy=metrics.get("condition_accuracy"),
                precision=metrics.get("condition_precision"),
                recall=metrics.get("condition_recall"),
                f1_score=metrics.get("condition_f1"),
                cross_validation_score=metrics.get("condition_cv_score"),
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.add(model_info)
            db.commit()
            print("Model training completed successfully!")
            print(f"Model saved to: {model_path}")
            print("Metrics:")
            for key, value in metrics.items():
                print(f"  {key}: {value:.4f}")

        except Exception as e:
            db.rollback()
            print(f"Error updating database: {str(e)}")
            return False
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"Error during model training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Use command line argument if provided, otherwise default
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data/symptom_data.csv"
    success = train_model(data_path)
    if success:
        print("\n[OK] Model training completed successfully!")
    else:
        print("\n[ERROR] Model training failed!")
        sys.exit(1)