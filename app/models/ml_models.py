from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.sql import func

from app.database import Base


class SymptomCondition(Base):
    """Knowledge base for symptom-condition relationships"""
    __tablename__ = "symptom_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    condition_name = Column(String(255), nullable=False, index=True)
    condition_code = Column(String(20), index=True)  # ICD-10 code if available
    symptoms = Column(JSON, nullable=False)  # List of symptoms with probabilities
    urgency_level = Column(Integer, default=1)  # 1-5 scale
    specialist_required = Column(String(100))  # Type of specialist needed
    common_age_groups = Column(JSON)  # Age ranges where condition is common
    gender_bias = Column(String(10))  # M/F/None if condition has gender bias
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SymptomChecker(Base):
    """Store symptom checker interactions and results"""
    __tablename__ = "symptom_checker_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)  # Optional - can be anonymous
    
    # Input data
    initial_symptoms = Column(JSON, nullable=False)  # List of initial symptoms
    additional_info = Column(JSON)  # Age, gender, medical history, etc.
    follow_up_responses = Column(JSON)  # Responses to follow-up questions
    
    # Results
    predicted_conditions = Column(JSON)  # List with probabilities
    urgency_score = Column(Float)  # 0-1 scale
    recommendations = Column(JSON)  # Next steps, specialist referrals
    
    # Feedback (for model improvement)
    user_feedback = Column(JSON)
    actual_diagnosis = Column(String(255))  # If provided later
    was_accurate = Column(Boolean)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class MLModel(Base):
    """Track ML model versions and performance"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Training information
    training_data_size = Column(Integer)
    features_used = Column(JSON)
    hyperparameters = Column(JSON)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    cross_validation_score = Column(Float)
    
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MLModel(name='{self.model_name}', version='{self.version}', active={self.is_active})>"