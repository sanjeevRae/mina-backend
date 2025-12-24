from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MedicalRecordBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    doctor_id: Optional[int] = None
    record_type: str
    title: str
    description: Optional[str] = None
    symptoms: Optional[List[str]] = []
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    medications: Optional[List[Dict[str, Any]]] = []
    lab_results: Optional[Dict[str, Any]] = {}
    vital_signs: Optional[Dict[str, float]] = {}
    attachments: Optional[List[str]] = []
    record_date: datetime
    is_confidential: bool = False
    tags: Optional[List[str]] = []


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    medications: Optional[List[Dict[str, Any]]] = None
    lab_results: Optional[Dict[str, Any]] = None
    vital_signs: Optional[Dict[str, float]] = None
    attachments: Optional[List[str]] = None
    is_confidential: Optional[bool] = None
    tags: Optional[List[str]] = None


class MedicalRecordResponse(MedicalRecordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    medication_name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None
    prescribed_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    refills_remaining: int = 0
    pharmacy_notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionUpdate(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    refills_remaining: Optional[int] = None
    pharmacy_notes: Optional[str] = None


class PrescriptionResponse(PrescriptionBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class VitalSigns(BaseModel):
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    heart_rate: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None