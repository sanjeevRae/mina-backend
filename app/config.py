import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }
    
    # App Configuration
    APP_NAME: str = "Telemedicine Backend"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    SQLITE_URL: str = "sqlite:///./telemedicine.db"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"  # Alternative name for compatibility
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    CLOUDINARY_SECURE: bool = True
    
    # EmailJS Configuration
    EMAILJS_SERVICE_ID: Optional[str] = None
    EMAILJS_TEMPLATE_ID: Optional[str] = None
    EMAILJS_PUBLIC_KEY: Optional[str] = None
    EMAILJS_USER_ID: Optional[str] = None
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_SERVER_KEY: Optional[str] = None
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = None

    @property
    def firebase_service_account(self) -> Optional[dict]:
        """Load Firebase service account JSON if path is set"""
        if self.FIREBASE_SERVICE_ACCOUNT_PATH:
            try:
                import json
                with open(self.FIREBASE_SERVICE_ACCOUNT_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    # Feature Flags
    ENABLE_ML_FEATURES: bool = True
    ENABLE_VIDEO_CALLS: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = False
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    
    # ML Model Configuration
    MODEL_PATH: str = "./models/"
    SYNTHETIC_DATA_PATH: str = "./data/synthetic/"
    MEDICAL_DATA_PATH: str = "./data/medical/"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,doc,docx"
    
    @field_validator("ALLOWED_EXTENSIONS")
    @classmethod
    def validate_extensions(cls, v):
        return [ext.strip().lower() for ext in v.split(",")]
    
    @property
    def database_url(self) -> str:
        """Return the appropriate database URL based on environment"""
        return self.DATABASE_URL or self.SQLITE_URL
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    @property
    def model_directory(self) -> Path:
        """Get the model directory path"""
        path = Path(self.MODEL_PATH)
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def data_directory(self) -> Path:
        """Get the data directory path"""
        path = Path(self.SYNTHETIC_DATA_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()