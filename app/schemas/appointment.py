from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from ..models.appointment import AppointmentStatus, AppointmentType


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = 30
    appointment_type: AppointmentType = AppointmentType.VIDEO_CALL
    title: str
    description: Optional[str] = None
    symptoms: Optional[List[str]] = []
    urgency_level: int = 1
    
    @validator("urgency_level")
    def validate_urgency(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Urgency level must be between 1 and 5")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    appointment_type: Optional[AppointmentType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    urgency_level: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None


class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    room_id: Optional[str] = None
    meeting_link: Optional[str] = None
    completed_at: Optional[datetime] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include related user info
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class VideoCallStart(BaseModel):
    appointment_id: int


class VideoCallJoin(BaseModel):
    room_id: str
    user_id: int