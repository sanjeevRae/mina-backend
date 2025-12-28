from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_image_url = Column(String(500))
    address = Column(Text)
    emergency_contact = Column(String(20))
    medical_conditions = Column(JSON)
    allergies = Column(JSON)
    current_medications = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    patient_appointments = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    doctor_appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    medical_records = relationship("MedicalRecord", foreign_keys="MedicalRecord.patient_id", back_populates="patient")
    doctor_medical_records = relationship("MedicalRecord", foreign_keys="MedicalRecord.doctor_id", back_populates="doctor")
    prescriptions = relationship("Prescription", foreign_keys="Prescription.patient_id", back_populates="patient")
    doctor_prescriptions = relationship("Prescription", foreign_keys="Prescription.doctor_id", back_populates="doctor")
    sent_messages = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender")
    received_messages = relationship("ChatMessage", foreign_keys="ChatMessage.receiver_id", back_populates="receiver")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"