import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import gc
import requests
import zipfile

from app.config import settings
from app.database import get_db
from app.models.ml_models import SymptomCondition, SymptomChecker, MLModel
from app.schemas.ml_models import SymptomInput, PatientInfo, ConditionPrediction, FollowUpQuestion

logger = logging.getLogger(__name__)


class SymptomCheckerModel:
    """ML model for symptom checking and condition prediction using GitHub Releases ZIP"""

    def __init__(self):
        self.condition_classifier = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.model_downloaded = False
        self.local_model_dir = Path("./models")

        # GitHub Releases ZIP URL - YOUR MODEL
        self.model_zip_url = "https://github.com/sanjeevRae/mina-ml-model/releases/download/v1.0/symptom_model_package.zip"

    def download_and_extract_model(self):
        """Download and extract model ZIP from GitHub Releases"""
        if self.model_downloaded and self.local_model_dir.exists():
            logger.info("Model already downloaded and extracted")
            return True

        try:
            logger.info(f"Downloading model ZIP from: {self.model_zip_url}")

            # Create models directory
            self.local_model_dir.mkdir(exist_ok=True)

            # Download the ZIP file
            zip_path = self.local_model_dir / "model.zip"
            response = requests.get(self.model_zip_url, stream=True)
            response.raise_for_status()

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract the ZIP file
            logger.info("Extracting model files...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.local_model_dir)

            # Remove the ZIP file after extraction
            zip_path.unlink()

            # Check what was extracted
            extracted_files = list(self.local_model_dir.glob("*"))
            logger.info(f"Extracted files: {[f.name for f in extracted_files]}")

            self.model_downloaded = True
            return True

        except Exception as e:
            logger.error(f"Failed to download/extract model: {e}")
            return False

    def load_model(self):
        """Load the model from extracted files"""
        if not self.model_downloaded:
            if not self.download_and_extract_model():
                raise FileNotFoundError("Model not available and download/extraction failed")

        try:
            logger.info(f"Loading model from: {self.local_model_dir}")

            # Look for model files in the extracted directory
            model_files = list(self.local_model_dir.glob("*.joblib")) + list(self.local_model_dir.glob("*.pkl"))

            if not model_files:
                raise FileNotFoundError("No model files found in extracted directory")

            # Load the first model file found
            model_file = model_files[0]
            logger.info(f"Loading model file: {model_file}")

            model_data = joblib.load(model_file)

            # Handle different model formats
            if isinstance(model_data, dict):
                self.condition_classifier = model_data.get('condition_classifier')
                self.label_encoders = model_data.get('label_encoders', {})
                self.scaler = model_data.get('scaler')
                self.feature_columns = model_data.get('feature_columns', [])
            else:
                # Assume it's just the classifier
                self.condition_classifier = model_data
                logger.warning("Model loaded in simple format - some features may not work")

            if self.condition_classifier is None:
                raise ValueError("Failed to load model classifier")

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def predict(self, symptoms: List[SymptomInput], patient_info: Optional[PatientInfo] = None) -> Dict:
        """Predict conditions based on symptoms using the trained model"""
        # Ensure model is loaded
        if self.condition_classifier is None:
            self.load_model()

        if self.condition_classifier is None:
            raise ValueError("Model not available")

        # Prepare input data
        input_data = self._prepare_input(symptoms, patient_info)

        # Make predictions
        condition_probs = self.condition_classifier.predict_proba([input_data])[0]
        condition_classes = self.condition_classifier.classes_

        # Get top predictions
        top_indices = np.argsort(condition_probs)[-5:][::-1]  # Top 5
        predictions = []

        for idx in top_indices:
            if condition_probs[idx] > 0.01:  # Only include predictions with >1% probability
                condition = condition_classes[idx]

                predictions.append(ConditionPrediction(
                    condition_name=condition,
                    probability=float(condition_probs[idx]),
                    urgency_level=3,  # Default urgency level
                    specialist_recommended="general_practitioner",  # Default specialist
                    description=f"Based on your symptoms, this condition has a {condition_probs[idx]:.1%} probability"
                ))

        # Calculate overall confidence score
        confidence_score = float(max(condition_probs))

        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(symptoms, predictions)

        return {
            "predictions": predictions,
            "urgency_score": confidence_score,  # Use confidence as urgency score for now
            "follow_up_questions": follow_up_questions,
            "confidence_score": confidence_score
        }

    def _prepare_input(self, symptoms: List[SymptomInput], patient_info: Optional[PatientInfo]) -> List[float]:
        """Prepare input data for prediction based on the model's expected features."""
        # Create a zero-filled array with the same number of features as the model expects
        input_data = np.zeros(len(self.feature_columns))

        # Create a temporary dataframe with the expected structure
        temp_df = pd.DataFrame([input_data], columns=self.feature_columns)

        # Set symptom values if they exist in the feature columns
        for symptom_input in symptoms:
            symptom_name = symptom_input.symptom.lower().replace(" ", "_")
            # Check if the symptom column exists in our feature set
            if symptom_name in self.feature_columns:
                # Set the value for this symptom (using severity as the value)
                temp_df.loc[0, symptom_name] = symptom_input.severity
            # Also check for variations like "symptom_present" or "has_symptom"
            elif f"{symptom_name}_present" in self.feature_columns:
                temp_df.loc[0, f"{symptom_name}_present"] = 1
                if f"{symptom_name}_severity" in self.feature_columns:
                    temp_df.loc[0, f"{symptom_name}_severity"] = symptom_input.severity
            elif f"has_{symptom_name}" in self.feature_columns:
                temp_df.loc[0, f"has_{symptom_name}"] = 1

        # Handle patient info if provided
        if patient_info:
            if 'age' in self.feature_columns:
                temp_df.loc[0, 'age'] = patient_info.age or 0
            if 'gender' in self.feature_columns and patient_info.gender:
                # Encode gender if it's in the feature columns
                if 'gender' in self.label_encoders:
                    try:
                        temp_df.loc[0, 'gender'] = self.label_encoders['gender'].transform([patient_info.gender])[0]
                    except ValueError:
                        # If gender value is not in the encoder, use a default value
                        temp_df.loc[0, 'gender'] = 0
                else:
                    # If no encoder exists, use a default encoding
                    temp_df.loc[0, 'gender'] = 1 if patient_info.gender.lower() == 'male' else 0

        # Scale the input data using the fitted scaler
        input_scaled = self.scaler.transform(temp_df)

        # Return the first (and only) row as a list
        return input_scaled[0]

    def _generate_follow_up_questions(self, symptoms: List[SymptomInput], predictions: List[ConditionPrediction]) -> List[FollowUpQuestion]:
        """Generate follow-up questions to improve diagnosis accuracy"""
        questions = []

        # Ask about duration if not provided
        if any(s.duration_days is None for s in symptoms):
            questions.append(FollowUpQuestion(
                question="How long have you been experiencing these symptoms?",
                question_type="multiple_choice",
                options=["Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"]
            ))

        # Ask about fever if not mentioned but common in top predictions
        symptom_names = [s.symptom.lower() for s in symptoms]
        if not any("fever" in s for s in symptom_names):
            questions.append(FollowUpQuestion(
                question="Do you have a fever?",
                question_type="yes_no"
            ))

        # Ask about pain location if pain mentioned
        if any("pain" in s.symptom.lower() for s in symptoms):
            questions.append(FollowUpQuestion(
                question="On a scale of 1-10, how would you rate your pain?",
                question_type="scale"
            ))

        return questions[:3]  # Limit to 3 questions


def get_symptom_checker_model() -> SymptomCheckerModel:
    """Get or create the global symptom checker model instance"""
    return SymptomCheckerModel()
