import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from typing import List, Dict, Tuple, Any, Optional
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import logging

from config import settings
from database import get_db
from .models.ml_models import SymptomCondition, SymptomChecker, MLModel
from schemas.ml_models import SymptomInput, PatientInfo, ConditionPrediction, FollowUpQuestion

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generate synthetic medical data for training"""
    
    def __init__(self):
        self.symptom_condition_mapping = self._load_medical_knowledge()
        self.common_symptoms = [
            "fever", "headache", "cough", "fatigue", "sore_throat", "runny_nose",
            "body_aches", "nausea", "vomiting", "diarrhea", "chest_pain",
            "shortness_of_breath", "dizziness", "rash", "abdominal_pain",
            "joint_pain", "back_pain", "insomnia", "loss_of_appetite",
            "weight_loss", "weight_gain", "blurred_vision", "ear_pain",
            "difficulty_swallowing", "irregular_heartbeat", "excessive_thirst",
            "frequent_urination", "muscle_weakness", "numbness", "tingling"
        ]
        
    def _load_medical_knowledge(self) -> Dict[str, Dict]:
        """Load medical knowledge base from CDC/WHO data"""
        # This would normally load from real medical databases
        # For now, we'll create a comprehensive synthetic knowledge base
        return {
            "common_cold": {
                "symptoms": {
                    "runny_nose": 0.9, "sore_throat": 0.8, "cough": 0.7,
                    "headache": 0.6, "fatigue": 0.5, "body_aches": 0.4
                },
                "urgency": 1, "specialist": "general_practitioner",
                "age_groups": ["all"], "gender_bias": "none"
            },
            "influenza": {
                "symptoms": {
                    "fever": 0.95, "body_aches": 0.9, "fatigue": 0.9,
                    "headache": 0.8, "cough": 0.7, "sore_throat": 0.6
                },
                "urgency": 2, "specialist": "general_practitioner",
                "age_groups": ["all"], "gender_bias": "none"
            },
            "migraine": {
                "symptoms": {
                    "headache": 0.95, "nausea": 0.6, "blurred_vision": 0.4,
                    "dizziness": 0.3, "fatigue": 0.5
                },
                "urgency": 2, "specialist": "neurologist",
                "age_groups": ["adult"], "gender_bias": "female"
            },
            "pneumonia": {
                "symptoms": {
                    "cough": 0.9, "fever": 0.8, "shortness_of_breath": 0.7,
                    "chest_pain": 0.6, "fatigue": 0.7, "body_aches": 0.5
                },
                "urgency": 4, "specialist": "pulmonologist",
                "age_groups": ["elderly", "child"], "gender_bias": "none"
            },
            "hypertension": {
                "symptoms": {
                    "headache": 0.4, "dizziness": 0.3, "blurred_vision": 0.2,
                    "chest_pain": 0.2, "shortness_of_breath": 0.3
                },
                "urgency": 3, "specialist": "cardiologist",
                "age_groups": ["adult", "elderly"], "gender_bias": "none"
            },
            "diabetes_type_2": {
                "symptoms": {
                    "excessive_thirst": 0.7, "frequent_urination": 0.8,
                    "fatigue": 0.6, "weight_loss": 0.4, "blurred_vision": 0.3
                },
                "urgency": 3, "specialist": "endocrinologist",
                "age_groups": ["adult", "elderly"], "gender_bias": "none"
            },
            "anxiety_disorder": {
                "symptoms": {
                    "irregular_heartbeat": 0.6, "shortness_of_breath": 0.5,
                    "dizziness": 0.4, "insomnia": 0.7, "fatigue": 0.6
                },
                "urgency": 2, "specialist": "psychiatrist",
                "age_groups": ["adult"], "gender_bias": "female"
            }
        }
    
    def generate_patient_case(self, condition: str, num_symptoms: int = None) -> Dict:
        """Generate a synthetic patient case for a given condition"""
        if condition not in self.symptom_condition_mapping:
            raise ValueError(f"Unknown condition: {condition}")
        
        condition_data = self.symptom_condition_mapping[condition]
        symptoms_probs = condition_data["symptoms"]
        
        # Randomly select symptoms based on their probabilities
        if num_symptoms is None:
            num_symptoms = np.random.randint(2, 6)
        
        selected_symptoms = []
        symptom_list = list(symptoms_probs.keys())
        probabilities = list(symptoms_probs.values())
        
        # Select primary symptoms (high probability)
        primary_symptoms = [s for s, p in symptoms_probs.items() if p > 0.6]
        num_primary = min(num_symptoms // 2 + 1, len(primary_symptoms))
        selected_symptoms.extend(np.random.choice(primary_symptoms, num_primary, replace=False))
        
        # Add some secondary symptoms
        remaining_symptoms = [s for s in symptom_list if s not in selected_symptoms]
        num_secondary = min(num_symptoms - len(selected_symptoms), len(remaining_symptoms))
        if num_secondary > 0:
            selected_symptoms.extend(np.random.choice(remaining_symptoms, num_secondary, replace=False))
        
        # Generate symptom details
        symptoms = []
        for symptom in selected_symptoms:
            severity = np.random.randint(
                int(symptoms_probs.get(symptom, 0.3) * 6) + 1, 11
            )  # Higher probability = higher severity
            duration = np.random.randint(1, 30)  # Days
            symptoms.append({
                "symptom": symptom,
                "severity": severity,
                "duration_days": duration
            })
        
        # Generate patient demographics
        age = self._generate_age(condition_data["age_groups"])
        gender = self._generate_gender(condition_data["gender_bias"])
        
        return {
            "condition": condition,
            "symptoms": symptoms,
            "urgency_level": condition_data["urgency"],
            "specialist_required": condition_data["specialist"],
            "patient_info": {
                "age": age,
                "gender": gender,
                "existing_conditions": self._generate_comorbidities(condition, age),
                "current_medications": [],
                "allergies": []
            }
        }
    
    def _generate_age(self, age_groups: List[str]) -> int:
        """Generate age based on condition prevalence"""
        if "child" in age_groups:
            return np.random.randint(2, 18)
        elif "adult" in age_groups:
            return np.random.randint(18, 65)
        elif "elderly" in age_groups:
            return np.random.randint(65, 90)
        else:  # all ages
            return np.random.randint(2, 90)
    
    def _generate_gender(self, gender_bias: str) -> str:
        """Generate gender based on condition prevalence"""
        if gender_bias == "female":
            return np.random.choice(["female", "male"], p=[0.7, 0.3])
        elif gender_bias == "male":
            return np.random.choice(["male", "female"], p=[0.7, 0.3])
        else:
            return np.random.choice(["male", "female"])
    
    def _generate_comorbidities(self, primary_condition: str, age: int) -> List[str]:
        """Generate realistic comorbidities based on age and primary condition"""
        comorbidities = []
        
        if age > 50:
            if np.random.random() < 0.3:
                comorbidities.append("hypertension")
            if np.random.random() < 0.2:
                comorbidities.append("diabetes_type_2")
        
        if age > 65:
            if np.random.random() < 0.2:
                comorbidities.append("arthritis")
        
        return comorbidities
    
    def generate_dataset(self, num_samples: int = 10000) -> pd.DataFrame:
        """Generate a complete synthetic dataset"""
        data = []
        conditions = list(self.symptom_condition_mapping.keys())
        
        for _ in range(num_samples):
            condition = np.random.choice(conditions)
            case = self.generate_patient_case(condition)
            
            # Flatten the data for ML
            flattened = {
                "condition": case["condition"],
                "urgency_level": case["urgency_level"],
                "specialist_required": case["specialist_required"],
                "age": case["patient_info"]["age"],
                "gender": case["patient_info"]["gender"],
                "num_symptoms": len(case["symptoms"])
            }
            
            # Add symptom presence and severity
            all_symptoms_dict = {symptom: {"present": False, "severity": 0} 
                               for symptom in self.common_symptoms}
            
            for symptom_data in case["symptoms"]:
                symptom_name = symptom_data["symptom"]
                if symptom_name in all_symptoms_dict:
                    all_symptoms_dict[symptom_name]["present"] = True
                    all_symptoms_dict[symptom_name]["severity"] = symptom_data["severity"]
            
            # Add to flattened data
            for symptom in self.common_symptoms:
                flattened[f"{symptom}_present"] = all_symptoms_dict[symptom]["present"]
                flattened[f"{symptom}_severity"] = all_symptoms_dict[symptom]["severity"]
            
            data.append(flattened)
        
        return pd.DataFrame(data)


class SymptomCheckerModel:
    """ML model for symptom checking and condition prediction"""
    
    def __init__(self):
        self.condition_classifier = None
        self.urgency_classifier = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.data_generator = SyntheticDataGenerator()
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML training"""
        # Encode categorical variables
        categorical_columns = ["gender", "specialist_required"]
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col])
                else:
                    df[col] = self.label_encoders[col].transform(df[col])
        
        # Select feature columns
        symptom_columns = [col for col in df.columns if "_present" in col or "_severity" in col]
        feature_columns = ["age", "num_symptoms"] + categorical_columns + symptom_columns
        self.feature_columns = [col for col in feature_columns if col in df.columns]
        
        return df[self.feature_columns]
    
    def train(self, num_samples: int = 10000) -> Dict[str, float]:
        """Train the symptom checker models"""
        logger.info(f"Generating {num_samples} synthetic training samples...")
        
        # Generate synthetic data
        df = self.data_generator.generate_dataset(num_samples)
        
        # Prepare features and targets
        X = self.prepare_features(df.copy())
        y_condition = df["condition"]
        y_urgency = df["urgency_level"]
        
        # Split data
        X_train, X_test, y_condition_train, y_condition_test, y_urgency_train, y_urgency_test = \
            train_test_split(X, y_condition, y_urgency, test_size=0.2, random_state=42, stratify=y_condition)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train condition classifier
        logger.info("Training condition classifier...")
        self.condition_classifier = RandomForestClassifier(
            n_estimators=100, 
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.condition_classifier.fit(X_train_scaled, y_condition_train)
        
        # Train urgency classifier
        logger.info("Training urgency classifier...")
        self.urgency_classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.urgency_classifier.fit(X_train_scaled, y_urgency_train)
        
        # Evaluate models
        condition_pred = self.condition_classifier.predict(X_test_scaled)
        urgency_pred = self.urgency_classifier.predict(X_test_scaled)
        
        metrics = {
            "condition_accuracy": accuracy_score(y_condition_test, condition_pred),
            "condition_precision": precision_score(y_condition_test, condition_pred, average="weighted"),
            "condition_recall": recall_score(y_condition_test, condition_pred, average="weighted"),
            "condition_f1": f1_score(y_condition_test, condition_pred, average="weighted"),
            "urgency_accuracy": accuracy_score(y_urgency_test, urgency_pred),
            "urgency_f1": f1_score(y_urgency_test, urgency_pred, average="weighted")
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.condition_classifier, X_train_scaled, y_condition_train, cv=5)
        metrics["condition_cv_score"] = cv_scores.mean()
        
        logger.info(f"Training completed. Condition accuracy: {metrics['condition_accuracy']:.3f}")
        
        return metrics
    
    def save_model(self, version: str = None) -> str:
        """Save trained models to disk"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_dir = settings.model_directory
        model_path = model_dir / f"symptom_checker_v{version}"
        model_path.mkdir(exist_ok=True)
        
        # Save models
        joblib.dump(self.condition_classifier, model_path / "condition_classifier.joblib")
        joblib.dump(self.urgency_classifier, model_path / "urgency_classifier.joblib")
        joblib.dump(self.label_encoders, model_path / "label_encoders.joblib")
        joblib.dump(self.scaler, model_path / "scaler.joblib")
        joblib.dump(self.feature_columns, model_path / "feature_columns.joblib")
        
        logger.info(f"Models saved to {model_path}")
        return str(model_path)
    
    def load_model(self, model_path: str):
        """Load trained models from disk"""
        model_path = Path(model_path)
        
        self.condition_classifier = joblib.load(model_path / "condition_classifier.joblib")
        self.urgency_classifier = joblib.load(model_path / "urgency_classifier.joblib")
        self.label_encoders = joblib.load(model_path / "label_encoders.joblib")
        self.scaler = joblib.load(model_path / "scaler.joblib")
        self.feature_columns = joblib.load(model_path / "feature_columns.joblib")
        
        logger.info(f"Models loaded from {model_path}")
    
    def predict(self, symptoms: List[SymptomInput], patient_info: Optional[PatientInfo] = None) -> Dict:
        """Predict conditions based on symptoms"""
        if self.condition_classifier is None:
            raise ValueError("Model not trained or loaded")
        
        # Prepare input data
        input_data = self._prepare_input(symptoms, patient_info)
        
        # Make predictions
        condition_probs = self.condition_classifier.predict_proba([input_data])[0]
        condition_classes = self.condition_classifier.classes_
        urgency_pred = self.urgency_classifier.predict([input_data])[0]
        
        # Get top predictions
        top_indices = np.argsort(condition_probs)[-5:][::-1]  # Top 5
        predictions = []
        
        for idx in top_indices:
            if condition_probs[idx] > 0.05:  # Only include predictions with >5% probability
                condition = condition_classes[idx]
                condition_data = self.data_generator.symptom_condition_mapping.get(condition, {})
                
                predictions.append(ConditionPrediction(
                    condition_name=condition.replace("_", " ").title(),
                    probability=float(condition_probs[idx]),
                    urgency_level=int(urgency_pred),
                    specialist_recommended=condition_data.get("specialist", "general_practitioner"),
                    description=f"Based on your symptoms, this condition has a {condition_probs[idx]:.1%} probability"
                ))
        
        # Calculate overall urgency score
        urgency_score = float(urgency_pred / 5.0)  # Normalize to 0-1
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(symptoms, predictions)
        
        return {
            "predictions": predictions,
            "urgency_score": urgency_score,
            "follow_up_questions": follow_up_questions,
            "confidence_score": float(max(condition_probs))
        }
    
    def _prepare_input(self, symptoms: List[SymptomInput], patient_info: Optional[PatientInfo]) -> List[float]:
        """Prepare input data for prediction"""
        # Initialize feature vector
        input_data = {}
        
        # Patient info
        input_data["age"] = patient_info.age if patient_info and patient_info.age else 35
        input_data["gender"] = patient_info.gender if patient_info and patient_info.gender else "unknown"
        input_data["num_symptoms"] = len(symptoms)
        
        # Encode gender
        if "gender" in self.label_encoders:
            try:
                input_data["gender"] = self.label_encoders["gender"].transform([input_data["gender"]])[0]
            except ValueError:
                input_data["gender"] = 0  # Unknown
        
        # Initialize all symptoms as not present
        for symptom in self.data_generator.common_symptoms:
            input_data[f"{symptom}_present"] = False
            input_data[f"{symptom}_severity"] = 0
        
        # Set present symptoms
        for symptom_input in symptoms:
            symptom_name = symptom_input.symptom.lower().replace(" ", "_")
            if f"{symptom_name}_present" in input_data:
                input_data[f"{symptom_name}_present"] = True
                input_data[f"{symptom_name}_severity"] = symptom_input.severity
        
        # Convert to feature vector
        feature_vector = []
        for col in self.feature_columns:
            if col in input_data:
                feature_vector.append(float(input_data[col]))
            else:
                feature_vector.append(0.0)
        
        # Scale features
        return self.scaler.transform([feature_vector])[0]
    
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
        if "fever" not in symptom_names:
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