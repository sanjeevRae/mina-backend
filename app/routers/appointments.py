from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from database import get_db
from auth import get_current_user, require_doctor, require_patient
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from schemas.appointment import (
    AppointmentCreate, AppointmentResponse, AppointmentUpdate,
    AppointmentStatusUpdate, VideoCallStart, VideoCallJoin
)
from services.websocket_service import websocket_service
from services.notification_service import notification_service
import uuid

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    # Validate that patient and doctor exist
    patient = db.query(User).filter(
        User.id == appointment_data.patient_id,
        User.role == UserRole.PATIENT
    ).first()
    
    doctor = db.query(User).filter(
        User.id == appointment_data.doctor_id,
        User.role == UserRole.DOCTOR
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check authorization (patients can only book for themselves, doctors and admins can book for anyone)
    if current_user.role == UserRole.PATIENT and current_user.id != appointment_data.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only book appointments for yourself"
        )
    
    # Check for scheduling conflicts
    existing_appointment = db.query(Appointment).filter(
        and_(
            or_(
                Appointment.doctor_id == appointment_data.doctor_id,
                Appointment.patient_id == appointment_data.patient_id
            ),
            Appointment.scheduled_at == appointment_data.scheduled_at,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot already booked"
        )
    
    # Create appointment
    appointment = Appointment(**appointment_data.dict())
    
    # Generate room ID for video calls
    if appointment.appointment_type == AppointmentType.VIDEO_CALL:
        appointment.room_id = f"room_{uuid.uuid4().hex[:12]}"
        appointment.meeting_link = f"/video-call/{appointment.room_id}"
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Send notifications
    await notification_service.send_appointment_reminder(
        user_id=appointment.patient_id,
        appointment_id=appointment.id,
        appointment_time=appointment.scheduled_at,
        hours_before=24
    )
    
    # Include related data in response
    response_data = AppointmentResponse.from_orm(appointment)
    response_data.patient_name = patient.full_name
    response_data.doctor_name = doctor.full_name
    
    return response_data


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AppointmentStatus] = None,
    appointment_type: Optional[AppointmentType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List appointments with filters"""
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    )
    
    # Apply role-based filtering
    if current_user.role == UserRole.PATIENT:
        query = query.filter(Appointment.patient_id == current_user.id)
    elif current_user.role == UserRole.DOCTOR:
        query = query.filter(Appointment.doctor_id == current_user.id)
    # Admins can see all appointments
    
    # Apply filters
    if status:
        query = query.filter(Appointment.status == status)
    
    if appointment_type:
        query = query.filter(Appointment.appointment_type == appointment_type)
    
    if start_date:
        query = query.filter(Appointment.scheduled_at >= start_date)
    
    if end_date:
        query = query.filter(Appointment.scheduled_at <= end_date)
    
    if patient_id and current_user.role != UserRole.PATIENT:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    # Order by scheduled time
    query = query.order_by(Appointment.scheduled_at)
    
    appointments = query.offset(skip).limit(limit).all()
    
    # Build response with related data
    response_appointments = []
    for appointment in appointments:
        response_data = AppointmentResponse.from_orm(appointment)
        response_data.patient_name = appointment.patient.full_name
        response_data.doctor_name = appointment.doctor.full_name
        response_appointments.append(response_data)
    
    return response_appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific appointment"""
    appointment = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    elif current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    response_data = AppointmentResponse.from_orm(appointment)
    response_data.patient_name = appointment.patient.full_name
    response_data.doctor_name = appointment.doctor.full_name
    
    return response_data


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment"""
    appointment = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.PATIENT:
        if appointment.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Patients can only update limited fields
        allowed_fields = {"symptoms", "urgency_level"}
        update_data = {k: v for k, v in appointment_data.dict(exclude_unset=True).items() 
                      if k in allowed_fields}
    elif current_user.role == UserRole.DOCTOR:
        if appointment.doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        update_data = appointment_data.dict(exclude_unset=True)
    else:  # Admin
        update_data = appointment_data.dict(exclude_unset=True)
    
    # Update appointment
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    response_data = AppointmentResponse.from_orm(appointment)
    response_data.patient_name = appointment.patient.full_name
    response_data.doctor_name = appointment.doctor.full_name
    
    return response_data


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status_data: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    appointment = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization - only doctors and admins can update status
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and admins can update appointment status"
        )
    
    if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update status
    appointment.status = status_data.status
    
    if status_data.status == AppointmentStatus.COMPLETED:
        appointment.completed_at = datetime.utcnow()
    
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    # Send notification to patient
    await websocket_service.send_notification(
        user_id=appointment.patient_id,
        notification_data={
            "type": "appointment_status_updated",
            "appointment_id": appointment.id,
            "new_status": status_data.status.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    response_data = AppointmentResponse.from_orm(appointment)
    response_data.patient_name = appointment.patient.full_name
    response_data.doctor_name = appointment.doctor.full_name
    
    return response_data


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    elif current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update status to cancelled instead of deleting
    appointment.status = AppointmentStatus.CANCELLED
    appointment.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}


@router.post("/{appointment_id}/start-video-call")
async def start_video_call(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a video call for appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if current_user.id not in [appointment.patient_id, appointment.doctor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if appointment.appointment_type != AppointmentType.VIDEO_CALL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This appointment is not a video call"
        )
    
    # Create video room if not exists
    if not appointment.room_id:
        appointment.room_id = f"room_{uuid.uuid4().hex[:12]}"
        appointment.meeting_link = f"/video-call/{appointment.room_id}"
        db.commit()
    
    # Create video room in WebSocket service
    room_id = await websocket_service.video_call_manager.create_video_room(
        appointment_id=appointment.id,
        doctor_id=appointment.doctor_id,
        patient_id=appointment.patient_id
    )
    
    return {
        "room_id": room_id,
        "meeting_link": appointment.meeting_link,
        "appointment_id": appointment.id
    }


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming appointments for current user"""
    now = datetime.utcnow()
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(
        Appointment.scheduled_at > now,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
    )
    
    if current_user.role == UserRole.PATIENT:
        query = query.filter(Appointment.patient_id == current_user.id)
    elif current_user.role == UserRole.DOCTOR:
        query = query.filter(Appointment.doctor_id == current_user.id)
    
    appointments = query.order_by(Appointment.scheduled_at).limit(10).all()
    
    response_appointments = []
    for appointment in appointments:
        response_data = AppointmentResponse.from_orm(appointment)
        response_data.patient_name = appointment.patient.full_name
        response_data.doctor_name = appointment.doctor.full_name
        response_appointments.append(response_data)
    
    return response_appointments