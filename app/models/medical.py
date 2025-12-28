from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    
    record_type = Column(String(50), nullable=False)  # consultation, lab_result, imaging, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Medical data
    symptoms = Column(JSON)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    medications = Column(JSON)
    lab_results = Column(JSON)
    vital_signs = Column(JSON)  # blood pressure, heart rate, temperature, etc.
    
    # File attachments
    attachments = Column(JSON)  # List of file URLs
    
    # Metadata
    record_date = Column(DateTime(timezone=True), nullable=False)
    is_confidential = Column(Boolean, default=False)
    tags = Column(JSON)  # For easy searching/categorization
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="medical_records")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_id={self.patient_id}, type='{self.record_type}')>"


class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)  # e.g., "twice daily", "every 8 hours"
    duration = Column(String(100))  # e.g., "7 days", "2 weeks"
    instructions = Column(Text)
    
    prescribed_date = Column(DateTime(timezone=True), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True)
    refills_remaining = Column(Integer, default=0)
    pharmacy_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_prescriptions")
    appointment = relationship("Appointment", back_populates="prescriptions")
    
    def __repr__(self):
        return f"<Prescription(id={self.id}, patient_id={self.patient_id}, medication='{self.medication_name}')>"