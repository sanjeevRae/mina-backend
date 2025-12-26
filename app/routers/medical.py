from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from auth import get_current_user, get_current_active_user
from ..models.user import User
from ..models.medical import MedicalRecord, Prescription
from schemas.medical import (
    MedicalRecordCreate, 
    MedicalRecordUpdate, 
    MedicalRecordResponse,
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse
)

router = APIRouter(prefix="/medical", tags=["Medical Records & Prescriptions"])


# Medical Records Endpoints
@router.post("/records", response_model=MedicalRecordResponse)
async def create_medical_record(
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new medical record"""
    # Only doctors and admins can create medical records
    if current_user.role not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only doctors can create medical records")
    
    # Verify the doctor is authorized to create records for this patient
    if current_user.role == "DOCTOR" and record.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create records for your own patients")
    
    db_record = MedicalRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.get("/records", response_model=List[MedicalRecordResponse])
async def get_medical_records(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    record_type: Optional[str] = Query(None, description="Filter by record type"),
    start_date: Optional[date] = Query(None, description="Records from this date"),
    end_date: Optional[date] = Query(None, description="Records until this date"),
    limit: int = Query(50, le=100),
    skip: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get medical records with filtering"""
    query = db.query(MedicalRecord)
    
    # Apply role-based filtering
    if current_user.role == "PATIENT":
        # Patients can only see their own records
        query = query.filter(MedicalRecord.patient_id == current_user.id)
    elif current_user.role == "DOCTOR":
        # Doctors can see records for their patients or records they created
        query = query.filter(
            or_(
                MedicalRecord.doctor_id == current_user.id,
                MedicalRecord.patient_id.in_(
                    # Subquery to get patient IDs from doctor's appointments
                    db.query(MedicalRecord.patient_id).distinct()
                )
            )
        )
    # ADMIN can see all records (no additional filter)
    
    # Apply optional filters
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    if record_type:
        query = query.filter(MedicalRecord.record_type == record_type)
    if start_date:
        query = query.filter(MedicalRecord.record_date >= start_date)
    if end_date:
        query = query.filter(MedicalRecord.record_date <= end_date)
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific medical record"""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Check permissions
    if current_user.role == "PATIENT" and record.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "DOCTOR" and record.doctor_id != current_user.id and record.patient_id not in []:
        # Check if doctor has treated this patient
        raise HTTPException(status_code=403, detail="Access denied")
    
    return record


@router.put("/records/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_update: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a medical record"""
    if current_user.role not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only doctors can update medical records")
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Check permissions
    if current_user.role == "DOCTOR" and record.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own records")
    
    # Update fields
    update_data = record_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    
    return record


# Prescription Endpoints
@router.post("/prescriptions", response_model=PrescriptionResponse)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new prescription"""
    if current_user.role not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions")
    
    # Verify the doctor is authorized
    if current_user.role == "DOCTOR" and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create prescriptions as yourself")
    
    db_prescription = Prescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    
    return db_prescription


@router.get("/prescriptions", response_model=List[PrescriptionResponse])
async def get_prescriptions(
    patient_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    skip: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get prescriptions with filtering"""
    query = db.query(Prescription)
    
    # Apply role-based filtering
    if current_user.role == "PATIENT":
        query = query.filter(Prescription.patient_id == current_user.id)
    elif current_user.role == "DOCTOR":
        query = query.filter(Prescription.doctor_id == current_user.id)
    
    # Apply optional filters
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(Prescription.is_active == is_active)
    
    prescriptions = query.offset(skip).limit(limit).all()
    return prescriptions


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific prescription"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check permissions
    if current_user.role == "PATIENT" and prescription.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "DOCTOR" and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return prescription


@router.put("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: int,
    prescription_update: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a prescription"""
    if current_user.role not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only doctors can update prescriptions")
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check permissions
    if current_user.role == "DOCTOR" and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own prescriptions")
    
    # Update fields
    update_data = prescription_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)
    
    prescription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prescription)
    
    return prescription


@router.delete("/prescriptions/{prescription_id}")
async def deactivate_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate a prescription (soft delete)"""
    if current_user.role not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only doctors can deactivate prescriptions")
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check permissions
    if current_user.role == "DOCTOR" and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only deactivate your own prescriptions")
    
    prescription.is_active = False
    prescription.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Prescription deactivated successfully"}


@router.get("/records/types")
async def get_record_types():
    """Get available medical record types"""
    return {
        "record_types": [
            "consultation",
            "diagnosis", 
            "lab_results",
            "imaging",
            "procedure",
            "vaccination",
            "allergy",
            "medication_history",
            "emergency",
            "referral",
            "discharge_summary",
            "follow_up"
        ]
    }