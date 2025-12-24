#!/usr/bin/env python3
"""
Database initialization and setup script
"""

import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.database import init_db, SessionLocal
from app.models.user import User, UserRole
from app.models.ml_models import SymptomCondition
from app.auth import get_password_hash
from app.services.ml_service import SyntheticDataGenerator


def create_sample_users():
    """Create sample users for testing"""
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_user:
            # Create admin user
            admin = User(
                email="admin@telemedicine.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(admin)
        
        # Create sample doctor
        doctor_exists = db.query(User).filter(
            User.email == "doctor@telemedicine.com"
        ).first()
        
        if not doctor_exists:
            doctor = User(
                email="doctor@telemedicine.com",
                username="drdoe",
                full_name="Dr. John Doe",
                hashed_password=get_password_hash("doctor123"),
                role=UserRole.DOCTOR,
                is_active=True,
                is_verified=True,
                phone="+1234567890",
                created_at=datetime.utcnow()
            )
            db.add(doctor)
        
        # Create sample patient
        patient_exists = db.query(User).filter(
            User.email == "patient@telemedicine.com"
        ).first()
        
        if not patient_exists:
            patient = User(
                email="patient@telemedicine.com",
                username="patient",
                full_name="Jane Smith",
                hashed_password=get_password_hash("patient123"),
                role=UserRole.PATIENT,
                is_active=True,
                is_verified=True,
                phone="+1234567891",
                date_of_birth=datetime(1990, 5, 15),
                gender="female",
                medical_conditions=["hypertension"],
                allergies=["penicillin"],
                current_medications=["lisinopril 10mg"],
                created_at=datetime.utcnow()
            )
            db.add(patient)
        
        db.commit()
        print("✅ Sample users created successfully")
        
    except Exception as e:
        print(f"❌ Error creating sample users: {str(e)}")
        db.rollback()
    finally:
        db.close()


def populate_medical_knowledge():
    """Populate the symptom-condition knowledge base"""
    db = SessionLocal()
    
    try:
        # Check if knowledge base already exists
        existing_conditions = db.query(SymptomCondition).count()
        if existing_conditions > 0:
            print("✅ Medical knowledge base already populated")
            return
        
        # Get medical knowledge from synthetic data generator
        data_generator = SyntheticDataGenerator()
        
        for condition_name, condition_data in data_generator.symptom_condition_mapping.items():
            symptom_condition = SymptomCondition(
                condition_name=condition_name.replace("_", " ").title(),
                symptoms=condition_data["symptoms"],
                urgency_level=condition_data["urgency"],
                specialist_required=condition_data["specialist"],
                common_age_groups=condition_data["age_groups"],
                gender_bias=condition_data["gender_bias"],
                description=f"Common condition characterized by various symptoms with urgency level {condition_data['urgency']}"
            )
            db.add(symptom_condition)
        
        db.commit()
        print("✅ Medical knowledge base populated successfully")
        
    except Exception as e:
        print(f"❌ Error populating medical knowledge: {str(e)}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main setup function"""
    print("🚀 Initializing Telemedicine Backend Database...")
    
    # Initialize database tables
    try:
        init_db()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return
    
    # Create sample users
    create_sample_users()
    
    # Populate medical knowledge base
    populate_medical_knowledge()
    
    print("\n🎉 Database setup completed!")
    print("\n📋 Sample Credentials:")
    print("Admin: admin@telemedicine.com / admin123")
    print("Doctor: doctor@telemedicine.com / doctor123") 
    print("Patient: patient@telemedicine.com / patient123")
    print("\n🌐 Access the API at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()