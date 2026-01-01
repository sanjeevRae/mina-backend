# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.medical import MedicalRecord, Prescription
from app.models.communication import ChatMessage, Notification

__all__ = [
    "User",
    "UserRole",
    "Appointment",
    "AppointmentStatus",
    "AppointmentType",
    "MedicalRecord",
    "Prescription",
    "ChatMessage",
    "Notification"
]
