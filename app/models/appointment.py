from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(enum.Enum):
    VIDEO_CALL = "video_call"
    CHAT = "chat"
    IN_PERSON = "in_person"


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(Enum(AppointmentType), default=AppointmentType.VIDEO_CALL)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    symptoms = Column(JSON)  # List of symptoms
    urgency_level = Column(Integer, default=1)  # 1-5 scale
    
    # Video call details
    room_id = Column(String(100))
    meeting_link = Column(String(500))
    
    # Completion details
    completed_at = Column(DateTime(timezone=True))
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    notes = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    prescriptions = relationship("Prescription", back_populates="appointment")
    medical_records = relationship("MedicalRecord", back_populates="appointment")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status='{self.status}')>"