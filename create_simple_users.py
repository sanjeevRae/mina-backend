"""
Simple user creation script that bypasses bcrypt issues
"""
import hashlib
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.user import User

def simple_hash(password: str) -> str:
    """Simple hash for testing purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_simple_users():
    """Create users with simple password hashing"""
    print("🔐 Creating sample users with simple hashing...")
    
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
            hashed_password=simple_hash("admin123"),
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
            hashed_password=simple_hash("doctor123"),
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
            hashed_password=simple_hash("patient123"), 
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
        print("\n⚠️  Note: Using simple SHA256 hashing for demo purposes")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    create_simple_users()