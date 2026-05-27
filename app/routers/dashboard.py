from datetime import datetime
from typing import Dict, Iterable, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.communication import ChatMessage, Notification
from app.models.rating import DoctorRating
from app.models.user import User, UserRole
from app.schemas.appointment import AppointmentResponse
from app.schemas.dashboard import (
    DashboardContact,
    DashboardConversation,
    DashboardUnreadSummary,
    DoctorDashboardResponse,
    DoctorProfileUpdate,
    DoctorRatingCreate,
    DoctorRatingResponse,
    PatientDashboardResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ACTIVE_APPOINTMENT_STATUSES = (
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.IN_PROGRESS,
)


def _require_role(current_user: User, *allowed_roles: UserRole) -> None:
    if current_user.role not in allowed_roles:
        allowed = ", ".join(role.value for role in allowed_roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This dashboard is only available for: {allowed}",
        )


def _serialize_appointment(appointment: Appointment) -> AppointmentResponse:
    response = AppointmentResponse.from_orm(appointment)
    response.patient_name = appointment.patient.full_name if appointment.patient else None
    response.doctor_name = appointment.doctor.full_name if appointment.doctor else None
    return response


def _get_unread_summary(current_user: User, db: Session) -> DashboardUnreadSummary:
    unread_messages = db.query(ChatMessage).filter(
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False,
    ).count()

    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return DashboardUnreadSummary(
        unread_messages=unread_messages,
        unread_notifications=unread_notifications,
        total_unread=unread_messages + unread_notifications,
    )


def _build_recent_conversations(
    current_user: User,
    db: Session,
    limit: int = 10,
) -> List[DashboardConversation]:
    messages = db.query(ChatMessage).filter(
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id,
        )
    ).order_by(ChatMessage.created_at.desc()).limit(200).all()

    latest_by_partner: Dict[int, ChatMessage] = {}
    for message in messages:
        partner_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        if partner_id not in latest_by_partner:
            latest_by_partner[partner_id] = message
        if len(latest_by_partner) >= limit:
            break

    if not latest_by_partner:
        return []

    partner_ids = list(latest_by_partner.keys())
    partners = {
        user.id: user
        for user in db.query(User).filter(User.id.in_(partner_ids)).all()
    }
    unread_counts = {
        sender_id: unread_count
        for sender_id, unread_count in db.query(
            ChatMessage.sender_id,
            func.count(ChatMessage.id),
        ).filter(
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.sender_id.in_(partner_ids),
            ChatMessage.is_read == False,
        ).group_by(ChatMessage.sender_id).all()
    }

    conversations: List[DashboardConversation] = []
    for partner_id, message in latest_by_partner.items():
        partner = partners.get(partner_id)
        if partner is None:
            continue

        conversations.append(
            DashboardConversation(
                partner_id=partner.id,
                partner_name=partner.full_name,
                partner_role=partner.role,
                last_message=message.content,
                last_message_time=message.created_at,
                last_message_sender=message.sender_id,
                unread_count=unread_counts.get(partner.id, 0),
                message_type=message.message_type,
                appointment_id=message.appointment_id,
            )
        )

    conversations.sort(key=lambda item: item.last_message_time, reverse=True)
    return conversations[:limit]


def _get_message_stats(
    current_user: User,
    contact_ids: Iterable[int],
    db: Session,
) -> tuple[Dict[int, datetime], Dict[int, int]]:
    ids = list(contact_ids)
    if not ids:
        return {}, {}

    relevant_messages = db.query(ChatMessage).filter(
        or_(
            and_(
                ChatMessage.sender_id == current_user.id,
                ChatMessage.receiver_id.in_(ids),
            ),
            and_(
                ChatMessage.receiver_id == current_user.id,
                ChatMessage.sender_id.in_(ids),
            ),
        )
    ).order_by(ChatMessage.created_at.desc()).all()

    latest_message_at: Dict[int, datetime] = {}
    for message in relevant_messages:
        partner_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        if partner_id not in latest_message_at:
            latest_message_at[partner_id] = message.created_at

    unread_counts = {
        sender_id: unread_count
        for sender_id, unread_count in db.query(
            ChatMessage.sender_id,
            func.count(ChatMessage.id),
        ).filter(
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.sender_id.in_(ids),
            ChatMessage.is_read == False,
        ).group_by(ChatMessage.sender_id).all()
    }

    return latest_message_at, unread_counts


def _get_next_appointments(
    current_user: User,
    contacts: List[User],
    db: Session,
) -> Dict[int, Appointment]:
    if not contacts:
        return {}

    contact_ids = [contact.id for contact in contacts]
    query = db.query(Appointment).filter(
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.scheduled_at >= datetime.utcnow(),
    ).order_by(Appointment.scheduled_at.asc())

    if current_user.role == UserRole.PATIENT:
        query = query.filter(
            Appointment.patient_id == current_user.id,
            Appointment.doctor_id.in_(contact_ids),
        )
        partner_getter = lambda appointment: appointment.doctor_id
    else:
        query = query.filter(
            Appointment.doctor_id == current_user.id,
            Appointment.patient_id.in_(contact_ids),
        )
        partner_getter = lambda appointment: appointment.patient_id

    next_appointments: Dict[int, Appointment] = {}
    for appointment in query.all():
        partner_id = partner_getter(appointment)
        if partner_id not in next_appointments:
            next_appointments[partner_id] = appointment

    return next_appointments


def _build_contacts(
    current_user: User,
    contacts: List[User],
    db: Session,
) -> List[DashboardContact]:
    contact_ids = [contact.id for contact in contacts]
    latest_message_at, unread_counts = _get_message_stats(current_user, contact_ids, db)
    next_appointments = _get_next_appointments(current_user, contacts, db)

    response_contacts: List[DashboardContact] = []
    for contact in contacts:
        next_appointment = next_appointments.get(contact.id)
        can_call = bool(
            next_appointment
            and next_appointment.appointment_type == AppointmentType.VIDEO_CALL
        )
        response_contacts.append(
            DashboardContact(
                id=contact.id,
                full_name=contact.full_name,
                email=contact.email,
                phone=contact.phone,
                gender=contact.gender,
                role=contact.role,
                profile_image_url=contact.profile_image_url,
                specialization=contact.specialization,
                rating=contact.rating or 0.0,
                rating_count=contact.rating_count or 0,
                is_verified=contact.is_verified,
                can_chat=True,
                can_call=can_call,
                unread_messages=unread_counts.get(contact.id, 0),
                last_message_at=latest_message_at.get(contact.id),
                next_appointment_id=next_appointment.id if next_appointment else None,
                next_appointment_at=next_appointment.scheduled_at if next_appointment else None,
                next_appointment_type=next_appointment.appointment_type if next_appointment else None,
                next_appointment_status=next_appointment.status if next_appointment else None,
            )
        )

    response_contacts.sort(
        key=lambda item: (
            item.next_appointment_at is None,
            item.next_appointment_at.timestamp() if item.next_appointment_at else float("inf"),
            item.full_name.lower(),
        )
    )
    return response_contacts


def _get_patient_directory(current_user: User, db: Session) -> List[User]:
    appointment_patient_ids = [
        patient_id
        for (patient_id,) in db.query(Appointment.patient_id).filter(
            Appointment.doctor_id == current_user.id
        ).distinct().all()
    ]

    message_rows = db.query(
        ChatMessage.sender_id,
        ChatMessage.receiver_id,
    ).filter(
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id,
        )
    ).all()

    message_patient_ids = {
        receiver_id if sender_id == current_user.id else sender_id
        for sender_id, receiver_id in message_rows
        if (receiver_id if sender_id == current_user.id else sender_id) != current_user.id
    }

    patient_ids = sorted(set(appointment_patient_ids) | message_patient_ids)
    if not patient_ids:
        return []

    return db.query(User).filter(
        User.id.in_(patient_ids),
        User.role == UserRole.PATIENT,
        User.is_active == True,
    ).order_by(User.full_name.asc()).all()


def _get_doctor_directory(db: Session) -> List[User]:
    return db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.is_active == True,
    ).order_by(User.full_name.asc()).all()


def _get_upcoming_appointments_for_patient(current_user: User, db: Session) -> List[AppointmentResponse]:
    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
    ).filter(
        Appointment.patient_id == current_user.id,
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.scheduled_at >= datetime.utcnow(),
    ).order_by(Appointment.scheduled_at.asc()).limit(20).all()

    return [_serialize_appointment(appointment) for appointment in appointments]


def _get_schedule_for_doctor(current_user: User, db: Session) -> List[AppointmentResponse]:
    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
    ).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.scheduled_at >= datetime.utcnow(),
    ).order_by(Appointment.scheduled_at.asc()).limit(20).all()

    return [_serialize_appointment(appointment) for appointment in appointments]


@router.get("/patient", response_model=PatientDashboardResponse)
async def get_patient_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Patient dashboard data: doctor directory, appointments, and recent chats."""
    _require_role(current_user, UserRole.PATIENT)
    doctors = _get_doctor_directory(db)

    return PatientDashboardResponse(
        doctors=_build_contacts(current_user, doctors, db),
        upcoming_appointments=_get_upcoming_appointments_for_patient(current_user, db),
        recent_conversations=_build_recent_conversations(current_user, db),
        unread=_get_unread_summary(current_user, db),
    )


@router.get("/doctor", response_model=DoctorDashboardResponse)
async def get_doctor_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Doctor dashboard data: patient directory, schedule, and recent chats."""
    _require_role(current_user, UserRole.DOCTOR)
    patients = _get_patient_directory(current_user, db)

    return DoctorDashboardResponse(
        patients=_build_contacts(current_user, patients, db),
        schedule=_get_schedule_for_doctor(current_user, db),
        recent_conversations=_build_recent_conversations(current_user, db),
        unread=_get_unread_summary(current_user, db),
    )


@router.put("/doctor/profile", response_model=DashboardContact)
async def update_doctor_dashboard_profile(
    profile: DoctorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allow doctors to update dashboard profile fields."""
    _require_role(current_user, UserRole.DOCTOR)

    current_user.specialization = profile.specialization.strip()
    db.commit()
    db.refresh(current_user)

    return DashboardContact(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        gender=current_user.gender,
        role=current_user.role,
        profile_image_url=current_user.profile_image_url,
        specialization=current_user.specialization,
        rating=current_user.rating or 0.0,
        rating_count=current_user.rating_count or 0,
        is_verified=current_user.is_verified,
        can_chat=True,
        can_call=False,
    )


@router.post("/doctors/{doctor_id}/rating", response_model=DoctorRatingResponse)
async def rate_doctor(
    doctor_id: int,
    rating_data: DoctorRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the current patient's rating for a doctor."""
    _require_role(current_user, UserRole.PATIENT)

    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == UserRole.DOCTOR,
        User.is_active == True,
    ).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    rating = db.query(DoctorRating).filter(
        DoctorRating.doctor_id == doctor_id,
        DoctorRating.patient_id == current_user.id,
    ).first()

    if rating:
        rating.rating = rating_data.rating
        rating.comment = rating_data.comment
    else:
        rating = DoctorRating(
            doctor_id=doctor_id,
            patient_id=current_user.id,
            rating=rating_data.rating,
            comment=rating_data.comment,
        )
        db.add(rating)

    db.flush()

    average_rating, rating_count = db.query(
        func.avg(DoctorRating.rating),
        func.count(DoctorRating.id),
    ).filter(DoctorRating.doctor_id == doctor_id).one()

    doctor.rating = round(float(average_rating or 0), 2)
    doctor.rating_count = int(rating_count or 0)
    db.commit()
    db.refresh(rating)
    db.refresh(doctor)

    return DoctorRatingResponse(
        doctor_id=doctor.id,
        patient_id=current_user.id,
        rating=rating.rating,
        average_rating=doctor.rating or 0.0,
        rating_count=doctor.rating_count or 0,
        comment=rating.comment,
    )
