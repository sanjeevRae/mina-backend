"""
Schemas for Symptom Checker API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SymptomInput(BaseModel):
    """Input schema for symptom checking"""
    symptoms: List[str] = Field(
        ...,
        description="List of symptoms (e.g., ['fever', 'cough', 'fatigue'])",
        min_items=1,
        max_items=20,
        example=["fever", "cough", "fatigue", "sore throat"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fever", "cough", "fatigue", "sore throat"]
            }
        }


class ConditionPrediction(BaseModel):
    """Single condition prediction"""
    condition: str = Field(..., description="Name of the predicted condition")
    confidence: float = Field(..., description="Confidence score (0-100%)")
    severity: str = Field(..., description="Severity level: mild, moderate, or serious")
    recommendations: List[str] = Field(..., description="Wellness recommendations")
    matched_symptoms: List[str] = Field(..., description="Symptoms that match this condition")


class SymptomCheckResult(BaseModel):
    """Result of symptom check analysis"""
    predictions: List[ConditionPrediction] = Field(..., description="Top condition predictions")
    valid_symptoms: List[str] = Field(..., description="Recognized symptoms from input")
    unknown_symptoms: List[str] = Field(default=[], description="Unrecognized symptoms")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    disclaimer: str = Field(
        default="This is an AI-based suggestion and not a medical diagnosis. Always consult a healthcare professional for proper medical advice.",
        description="Medical disclaimer"
    )


class WellnessAdvice(BaseModel):
    """General wellness advice based on symptoms"""
    primary_condition: str = Field(..., description="Most likely condition")
    confidence: float = Field(..., description="Confidence percentage")
    severity: str = Field(..., description="Severity level")
    recommendations: List[str] = Field(..., description="Specific recommendations")
    general_advice: List[str] = Field(..., description="General health advice")
    when_to_seek_help: List[str] = Field(..., description="When to seek medical attention")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class SymptomListResponse(BaseModel):
    """Response containing all available symptoms"""
    symptoms: List[str] = Field(..., description="All recognized symptoms")
    count: int = Field(..., description="Total number of symptoms")


class ConditionInfoResponse(BaseModel):
    """Detailed information about a specific condition"""
    condition: str = Field(..., description="Condition name")
    symptoms: List[str] = Field(..., description="Typical symptoms")
    severity: str = Field(..., description="Severity level")
    recommendations: List[str] = Field(..., description="Wellness recommendations")
