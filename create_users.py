"""
Create sample users for the telemedicine system
"""
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.user import User
from app.auth import get_password_hash

def create_sample_users():
    """Create sample users for testing"""
    print("🔐 Creating sample users...")
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_admin = db.query(User).filter(User.email == "admin@telemedicine.com").first()
        if existing_admin:
            print("✅ Sample users already exist")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@telemedicine.com",
            username="admin",
            hashed_password=get_password_hash("admin123"[:72]),  # Truncate password
            full_name="System Administrator",
            role="ADMIN",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        
        # Create doctor user
        doctor_user = User(
            email="doctor@telemedicine.com", 
            username="doctor",
            hashed_password=get_password_hash("doctor123"[:72]),  # Truncate password
            full_name="Dr. John Smith",
            role="DOCTOR",
            is_active=True,
            is_verified=True,
            phone="+1234567890"
        )
        db.add(doctor_user)
        
        # Create patient user
        patient_user = User(
            email="patient@telemedicine.com",
            username="patient", 
            hashed_password=get_password_hash("patient123"[:72]),  # Truncate password
            full_name="Jane Doe",
            role="PATIENT",
            is_active=True,
            is_verified=True,
            phone="+0987654321"
        )
        db.add(patient_user)
        
        db.commit()
        print("✅ Sample users created successfully!")
        print("\n📋 Credentials:")
        print("Admin: admin@telemedicine.com / admin123")
        print("Doctor: doctor@telemedicine.com / doctor123") 
        print("Patient: patient@telemedicine.com / patient123")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database
    init_db()
    create_sample_users()