from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from app.models.user import User
from app.models.ml_models import SymptomChecker, MLModel
from schemas.ml_models import (
    SymptomCheckerStart, SymptomCheckerSession, SymptomCheckerResult,
    SymptomCheckerFeedback, MLModelInfo, ModelTrainingRequest
)
from services.ml_service import get_symptom_checker_model
import uuid
import asyncio
import logging

router = APIRouter(prefix="/ml", tags=["machine learning"])
logger = logging.getLogger(__name__)


@router.post("/symptom-checker/start", response_model=SymptomCheckerResult)
async def start_symptom_checker(
    symptom_data: SymptomCheckerStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a symptom checker session"""
    try:
        # Get ML model
        ml_model = get_symptom_checker_model()
        
        # Check if model is trained
        if ml_model.condition_classifier is None:
            # Try to load existing model
            try:
                # Look for the latest model
                latest_model = db.query(MLModel).filter(
                    MLModel.model_name == "symptom_checker",
                    MLModel.is_active == True
                ).order_by(MLModel.created_at.desc()).first()
                
                if latest_model:
                    ml_model.load_model(latest_model.file_path)
                else:
                    # Train a new model
                    logger.info("No trained model found. Training new model...")
                    training_metrics = ml_model.train(num_samples=5000)  # Smaller sample for faster training
                    
                    # Save the model
                    model_path = ml_model.save_model()
                    
                    # Save model info to database
                    model_info = MLModel(
                        model_name="symptom_checker",
                        version="1.0.0",
                        file_path=model_path,
                        training_data_size=5000,
                        features_used=ml_model.feature_columns,
                        accuracy=training_metrics.get("condition_accuracy"),
                        precision=training_metrics.get("condition_precision"),
                        recall=training_metrics.get("condition_recall"),
                        f1_score=training_metrics.get("condition_f1"),
                        cross_validation_score=training_metrics.get("condition_cv_score"),
                        is_active=True
                    )
                    
                    db.add(model_info)
                    db.commit()
                    
                    logger.info(f"Model trained successfully. Accuracy: {training_metrics.get('condition_accuracy', 0):.3f}")
                    
            except Exception as e:
                logger.error(f"Error loading/training model: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="ML model is not available. Please try again later."
                )
        
        # Generate session ID
        session_id = f"symptom_{uuid.uuid4().hex[:16]}"
        
        # Make prediction
        prediction_result = ml_model.predict(
            symptoms=symptom_data.initial_symptoms,
            patient_info=symptom_data.patient_info
        )
        
        # Store session in database
        session = SymptomChecker(
            session_id=session_id,
            user_id=current_user.id,
            initial_symptoms=[s.dict() for s in symptom_data.initial_symptoms],
            additional_info=symptom_data.patient_info.dict() if symptom_data.patient_info else {},
            predicted_conditions=[p.dict() for p in prediction_result["predictions"]],
            urgency_score=prediction_result["urgency_score"],
            recommendations=_generate_recommendations(prediction_result)
        )
        
        db.add(session)
        db.commit()
        
        # Build response
        result = SymptomCheckerResult(
            session_id=session_id,
            predicted_conditions=prediction_result["predictions"],
            urgency_score=prediction_result["urgency_score"],
            recommendations=_generate_recommendations(prediction_result),
            follow_up_questions=prediction_result.get("follow_up_questions", []),
            confidence_score=prediction_result["confidence_score"]
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in symptom checker: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing symptoms. Please try again later."
        )


@router.post("/symptom-checker/continue", response_model=SymptomCheckerResult)
async def continue_symptom_checker(
    session_data: SymptomCheckerSession,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Continue symptom checker session with follow-up responses"""
    # Get session
    session = db.query(SymptomChecker).filter(
        SymptomChecker.session_id == session_data.session_id,
        SymptomChecker.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update session with follow-up responses
    if not session.follow_up_responses:
        session.follow_up_responses = []
    
    session.follow_up_responses.extend([r.dict() for r in session_data.follow_up_responses])
    
    # Re-run prediction with additional information
    ml_model = get_symptom_checker_model()
    
    # Convert stored symptoms back to SymptomInput format
    from app.schemas.ml_models import SymptomInput, PatientInfo
    symptoms = [SymptomInput(**s) for s in session.initial_symptoms]
    patient_info = PatientInfo(**session.additional_info) if session.additional_info else None
    
    # Make refined prediction
    prediction_result = ml_model.predict(symptoms=symptoms, patient_info=patient_info)
    
    # Update session
    session.predicted_conditions = [p.dict() for p in prediction_result["predictions"]]
    session.urgency_score = prediction_result["urgency_score"]
    session.recommendations = _generate_recommendations(prediction_result)
    session.completed_at = datetime.utcnow()
    
    db.commit()
    
    # Build response
    result = SymptomCheckerResult(
        session_id=session.session_id,
        predicted_conditions=prediction_result["predictions"],
        urgency_score=prediction_result["urgency_score"],
        recommendations=_generate_recommendations(prediction_result),
        follow_up_questions=[],  # No more questions after follow-up
        confidence_score=prediction_result["confidence_score"]
    )
    
    return result


@router.post("/symptom-checker/feedback")
async def submit_feedback(
    feedback: SymptomCheckerFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for symptom checker session"""
    # Get session
    session = db.query(SymptomChecker).filter(
        SymptomChecker.session_id == feedback.session_id,
        SymptomChecker.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update session with feedback
    session.user_feedback = {
        "was_helpful": feedback.was_helpful,
        "comments": feedback.comments,
        "submitted_at": datetime.utcnow().isoformat()
    }
    
    if feedback.actual_diagnosis:
        session.actual_diagnosis = feedback.actual_diagnosis
        session.was_accurate = any(
            pred["condition_name"].lower() in feedback.actual_diagnosis.lower()
            for pred in session.predicted_conditions or []
        )
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}


@router.get("/symptom-checker/history", response_model=List[dict])
async def get_symptom_checker_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's symptom checker history"""
    sessions = db.query(SymptomChecker).filter(
        SymptomChecker.user_id == current_user.id
    ).order_by(SymptomChecker.created_at.desc()).offset(skip).limit(limit).all()
    
    history = []
    for session in sessions:
        history.append({
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "initial_symptoms": session.initial_symptoms,
            "predicted_conditions": session.predicted_conditions[:3] if session.predicted_conditions else [],  # Top 3
            "urgency_score": session.urgency_score,
            "was_helpful": session.user_feedback.get("was_helpful") if session.user_feedback else None
        })
    
    return history


@router.get("/models", response_model=List[MLModelInfo])
async def list_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List available ML models"""
    models = db.query(MLModel).order_by(MLModel.created_at.desc()).all()
    
    model_info = []
    for model in models:
        model_info.append(MLModelInfo(
            model_name=model.model_name,
            version=model.version,
            accuracy=model.accuracy,
            last_trained=model.created_at,
            is_active=model.is_active
        ))
    
    return model_info


@router.post("/train-model")
async def train_model(
    training_request: ModelTrainingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a new ML model (admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can train models"
        )
    
    try:
        # Start training in background (in production, use Celery or similar)
        job_id = f"training_{uuid.uuid4().hex[:12]}"
        
        # For now, train synchronously (in production, make this async)
        ml_model = get_symptom_checker_model()
        training_metrics = ml_model.train(num_samples=10000)
        
        # Save model
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = ml_model.save_model(version)
        
        # Deactivate old models
        db.query(MLModel).filter(
            MLModel.model_name == training_request.model_name,
            MLModel.is_active == True
        ).update({"is_active": False})
        
        # Save new model info
        model_info = MLModel(
            model_name=training_request.model_name,
            version=version,
            file_path=model_path,
            training_data_size=10000,
            features_used=ml_model.feature_columns,
            hyperparameters=training_request.hyperparameters,
            accuracy=training_metrics.get("condition_accuracy"),
            precision=training_metrics.get("condition_precision"),
            recall=training_metrics.get("condition_recall"),
            f1_score=training_metrics.get("condition_f1"),
            cross_validation_score=training_metrics.get("condition_cv_score"),
            is_active=True
        )
        
        db.add(model_info)
        db.commit()
        
        return {
            "job_id": job_id,
            "status": "completed",
            "model_name": training_request.model_name,
            "metrics": training_metrics
        }
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error training model"
        )


def _generate_recommendations(prediction_result: dict) -> List[str]:
    """Generate recommendations based on predictions"""
    recommendations = []
    
    urgency_score = prediction_result.get("urgency_score", 0)
    predictions = prediction_result.get("predictions", [])
    
    if urgency_score >= 0.8:
        recommendations.append("🚨 Seek immediate emergency medical attention")
    elif urgency_score >= 0.6:
        recommendations.append("⚠️ Contact your doctor or visit urgent care today")
    elif urgency_score >= 0.4:
        recommendations.append("📞 Schedule an appointment with your doctor within the next few days")
    else:
        recommendations.append("💡 Consider monitoring symptoms and contact healthcare provider if they worsen")
    
    # Add specific recommendations based on top predictions
    if predictions:
        top_condition = predictions[0]
        specialist = top_condition.specialist_recommended
        
        if specialist and specialist != "general_practitioner":
            recommendations.append(f"🏥 Consider consulting a {specialist.replace('_', ' ')}")
    
    # General health recommendations
    recommendations.extend([
        "💊 Keep track of your symptoms and any medications you're taking",
        "🌡️ Monitor your temperature and vital signs",
        "💧 Stay hydrated and get adequate rest",
        "⚠️ This is not a replacement for professional medical advice"
    ])
    
    return recommendations