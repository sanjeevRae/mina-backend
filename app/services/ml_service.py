import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from app.config import settings
from app.database import get_db
from app.models.ml_models import SymptomCondition, SymptomChecker, MLModel
from app.schemas.ml_models import SymptomInput, PatientInfo, ConditionPrediction, FollowUpQuestion

logger = logging.getLogger(__name__)


class SymptomCheckerModel:
    """ML model for symptom checking and condition prediction using real CSV data"""

    def __init__(self):
        self.condition_classifier = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self._auto_load_latest_model()

    def _auto_load_latest_model(self):
        """Automatically load the latest trained model from the models directory if available."""
        try:
            model_dir = settings.model_directory
            if not model_dir.exists() or not model_dir.is_dir():
                return
            # Find all symptom_checker_v* directories
            model_versions = [d for d in model_dir.iterdir() if d.is_dir() and d.name.startswith("symptom_checker_v")]
            if not model_versions:
                return
            # Sort by version (timestamp in name)
            latest_model = sorted(model_versions, key=lambda d: d.name, reverse=True)[0]
            self.load_model(str(latest_model))
            logger.info(f"Auto-loaded latest model: {latest_model}")
        except Exception as e:
            logger.warning(f"Could not auto-load latest model: {e}")

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from CSV data for ML training."""
        # Make a copy to avoid modifying the original dataframe
        df = df.copy()

        # Identify categorical and numerical columns
        categorical_columns = []
        numerical_columns = []

        for col in df.columns:
            if col != 'diagnosis':  # Target column
                if df[col].dtype == 'object' or col in ['gender', 'age_group']:  # Add other categorical columns as needed
                    categorical_columns.append(col)
                else:
                    numerical_columns.append(col)

        # Encode categorical variables
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[col] = self.label_encoders[col].transform(df[col].astype(str))

        # Identify feature columns (all except diagnosis)
        self.feature_columns = [col for col in df.columns if col != 'diagnosis']

        return df[self.feature_columns]

    def train(self, real_data_path: str = "data/symptom_data.csv") -> Dict[str, float]:
        """Train the symptom checker model using real CSV data."""
        if not os.path.exists(real_data_path):
            raise FileNotFoundError(f"CSV data file not found: {real_data_path}")

        logger.info(f"Loading real dataset from {real_data_path}...")
        df = pd.read_csv(real_data_path)

        # Validate that the dataset has the required 'diagnosis' column
        if 'diagnosis' not in df.columns:
            raise ValueError("CSV file must contain a 'diagnosis' column for the target variable")

        # Prepare features and target
        X = self.prepare_features(df)
        y = df['diagnosis']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train condition classifier
        logger.info("Training condition classifier...")
        self.condition_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.condition_classifier.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = self.condition_classifier.predict(X_test_scaled)
        metrics = {
            "condition_accuracy": accuracy_score(y_test, y_pred),
            "condition_precision": precision_score(y_test, y_pred, average="weighted"),
            "condition_recall": recall_score(y_test, y_pred, average="weighted"),
            "condition_f1": f1_score(y_test, y_pred, average="weighted"),
        }

        # Cross-validation
        cv_scores = cross_val_score(self.condition_classifier, X_train_scaled, y_train, cv=5)
        metrics["condition_cv_score"] = cv_scores.mean()

        logger.info(f"Training completed. Condition accuracy: {metrics['condition_accuracy']:.3f}")
        logger.info(f"Cross-validation score: {metrics['condition_cv_score']:.3f}")

        return metrics

    def save_model(self, version: str = None) -> str:
        """Save trained models to disk"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        model_dir = settings.model_directory
        model_path = model_dir / f"symptom_checker_v{version}"
        model_path.mkdir(exist_ok=True)

        # Save models
        if self.condition_classifier is not None:
            joblib.dump(self.condition_classifier, model_path / "condition_classifier.joblib")
        joblib.dump(self.label_encoders, model_path / "label_encoders.joblib")
        joblib.dump(self.scaler, model_path / "scaler.joblib")
        joblib.dump(self.feature_columns, model_path / "feature_columns.joblib")

        logger.info(f"Models saved to {model_path}")
        return str(model_path)

    def load_model(self, model_path: str):
        """Load trained models from disk"""
        model_path = Path(model_path)

        if (model_path / "condition_classifier.joblib").exists():
            self.condition_classifier = joblib.load(model_path / "condition_classifier.joblib")
        self.label_encoders = joblib.load(model_path / "label_encoders.joblib")
        self.scaler = joblib.load(model_path / "scaler.joblib")
        self.feature_columns = joblib.load(model_path / "feature_columns.joblib")

        logger.info(f"Models loaded from {model_path}")

    def predict(self, symptoms: List[SymptomInput], patient_info: Optional[PatientInfo] = None) -> Dict:
        """Predict conditions based on symptoms using the trained model"""
        if self.condition_classifier is None:
            raise ValueError("Model not trained or loaded")

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


# Global model instance
_symptom_checker_model = None

def get_symptom_checker_model() -> SymptomCheckerModel:
    """Get or create the global symptom checker model instance"""
    global _symptom_checker_model
    if _symptom_checker_model is None:
        _symptom_checker_model = SymptomCheckerModel()
    return _symptom_checker_model