from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.models.appointment import AppointmentStatus, AppointmentType
from app.models.user import UserRole
from app.schemas.appointment import AppointmentResponse


class DashboardContact(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[str] = None
    role: UserRole
    profile_image_url: Optional[str] = None
    is_verified: bool = False
    can_chat: bool = True
    can_call: bool = False
    unread_messages: int = 0
    last_message_at: Optional[datetime] = None
    next_appointment_id: Optional[int] = None
    next_appointment_at: Optional[datetime] = None
    next_appointment_type: Optional[AppointmentType] = None
    next_appointment_status: Optional[AppointmentStatus] = None


class DashboardConversation(BaseModel):
    partner_id: int
    partner_name: str
    partner_role: UserRole
    last_message: str
    last_message_time: datetime
    last_message_sender: int
    unread_count: int = 0
    message_type: str = "text"
    appointment_id: Optional[int] = None


class DashboardUnreadSummary(BaseModel):
    unread_messages: int = 0
    unread_notifications: int = 0
    total_unread: int = 0


class PatientDashboardResponse(BaseModel):
    doctors: List[DashboardContact]
    upcoming_appointments: List[AppointmentResponse]
    recent_conversations: List[DashboardConversation]
    unread: DashboardUnreadSummary


class DoctorDashboardResponse(BaseModel):
    patients: List[DashboardContact]
    schedule: List[AppointmentResponse]
    recent_conversations: List[DashboardConversation]
    unread: DashboardUnreadSummary
