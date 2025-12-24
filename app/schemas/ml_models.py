from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class SymptomInput(BaseModel):
    symptom: str
    severity: int  # 1-10 scale
    duration_days: Optional[int] = None
    
    @validator("severity")
    def validate_severity(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Severity must be between 1 and 10")
        return v


class PatientInfo(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    existing_conditions: Optional[List[str]] = []
    current_medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []


class SymptomCheckerStart(BaseModel):
    initial_symptoms: List[SymptomInput]
    patient_info: Optional[PatientInfo] = None


class FollowUpQuestion(BaseModel):
    question: str
    question_type: str  # yes_no, multiple_choice, scale, text
    options: Optional[List[str]] = None  # For multiple choice


class FollowUpResponse(BaseModel):
    question_id: str
    answer: Any  # Could be bool, str, int, etc.


class SymptomCheckerSession(BaseModel):
    session_id: str
    follow_up_responses: List[FollowUpResponse]


class ConditionPrediction(BaseModel):
    condition_name: str
    probability: float
    urgency_level: int
    specialist_recommended: Optional[str] = None
    description: Optional[str] = None


class SymptomCheckerResult(BaseModel):
    session_id: str
    predicted_conditions: List[ConditionPrediction]
    urgency_score: float  # 0-1 scale
    recommendations: List[str]
    follow_up_questions: Optional[List[FollowUpQuestion]] = []
    confidence_score: float


class SymptomCheckerFeedback(BaseModel):
    session_id: str
    was_helpful: bool
    actual_diagnosis: Optional[str] = None
    comments: Optional[str] = None


class MLModelInfo(BaseModel):
    model_name: str
    version: str
    accuracy: Optional[float] = None
    last_trained: datetime
    is_active: bool


class ModelTrainingRequest(BaseModel):
    model_name: str
    training_data_path: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = {}


class ModelTrainingResponse(BaseModel):
    job_id: str
    status: str  # started, running, completed, failed
    model_name: str
    estimated_completion: Optional[datetime] = None