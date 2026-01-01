"""
Symptom Checker API Router
AI-powered symptom analysis endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging

from app.schemas.symptom_checker import (
    SymptomInput,
    SymptomCheckResult,
    WellnessAdvice,
    SymptomListResponse,
    ConditionInfoResponse,
    ConditionPrediction
)
from app.services.ml_service import symptom_checker_service
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/symptom-checker", tags=["AI Symptom Checker"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=SymptomCheckResult)
async def analyze_symptoms(
    symptom_input: SymptomInput,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze symptoms and predict possible conditions
    
    **Note**: This is an AI-based suggestion tool, NOT a medical diagnosis.
    Always consult healthcare professionals for proper medical advice.
    """
    try:
        # Validate symptoms
        valid_symptoms, unknown_symptoms = symptom_checker_service.validate_symptoms(
            symptom_input.symptoms
        )
        
        if not valid_symptoms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No recognized symptoms provided. Use /symptom-checker/symptoms to see available symptoms."
            )
        
        # Get predictions
        predictions = symptom_checker_service.predict(valid_symptoms, top_k=3)
        
        # Convert to Pydantic models
        prediction_models = [ConditionPrediction(**pred) for pred in predictions]
        
        return SymptomCheckResult(
            predictions=prediction_models,
            valid_symptoms=valid_symptoms,
            unknown_symptoms=unknown_symptoms
        )
        
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze symptoms: {str(e)}"
        )


@router.post("/wellness-advice", response_model=WellnessAdvice)
async def get_wellness_advice(
    symptom_input: SymptomInput,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive wellness advice based on symptoms
    
    Provides personalized recommendations and guidance on when to seek medical help.
    """
    try:
        # Validate symptoms
        valid_symptoms, _ = symptom_checker_service.validate_symptoms(
            symptom_input.symptoms
        )
        
        if not valid_symptoms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No recognized symptoms provided."
            )
        
        # Get wellness advice
        advice = symptom_checker_service.get_wellness_advice(valid_symptoms)
        
        return WellnessAdvice(**advice)
        
    except Exception as e:
        logger.error(f"Error getting wellness advice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get wellness advice: {str(e)}"
        )


@router.get("/symptoms", response_model=SymptomListResponse)
async def get_available_symptoms():
    """
    Get list of all recognized symptoms
    
    Use these symptom names when analyzing symptoms for best results.
    """
    try:
        symptoms = symptom_checker_service.get_all_symptoms()
        return SymptomListResponse(
            symptoms=sorted(symptoms),
            count=len(symptoms)
        )
    except Exception as e:
        logger.error(f"Error getting symptoms list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve symptoms list"
        )


@router.get("/conditions/{condition_name}", response_model=ConditionInfoResponse)
async def get_condition_info(
    condition_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific medical condition
    
    Returns symptoms, severity, and wellness recommendations.
    """
    try:
        condition_info = symptom_checker_service.get_condition_info(condition_name)
        
        if not condition_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Condition '{condition_name}' not found in database"
            )
        
        return ConditionInfoResponse(
            condition=condition_name,
            symptoms=condition_info.get("symptoms", []),
            severity=condition_info.get("severity", "unknown"),
            recommendations=condition_info.get("recommendations", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting condition info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve condition information"
        )


@router.get("/health")
async def symptom_checker_health():
    """
    Health check for symptom checker service
    
    Returns model status and basic information.
    """
    try:
        # Try to load model if not loaded
        if symptom_checker_service.model is None:
            symptom_checker_service.load_model()
        
        return {
            "status": "healthy",
            "model_loaded": symptom_checker_service.model is not None,
            "num_symptoms": len(symptom_checker_service.symptoms_list) if symptom_checker_service.symptoms_list else 0,
            "num_conditions": len(symptom_checker_service.metadata['conditions']) if symptom_checker_service.metadata else 0,
            "message": "Symptom checker is ready"
        }
    except Exception as e:
        logger.error(f"Symptom checker health check failed: {e}")
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e),
            "message": "Model not loaded. Run train_symptom_model.py to train the model."
        }
