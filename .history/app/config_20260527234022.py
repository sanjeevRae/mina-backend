import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import ValidationInfo, field_validator


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }
    
    # App Configuration
    APP_NAME: str = "MINA Backend"
    DEBUG: bool = False
    ENABLE_DOCS: Optional[bool] = None
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    BASE_URL: Optional[str] = None  # Your Render deployment URL
    MODEL_PATH: str = "./models"
    SYNTHETIC_DATA_PATH: str = "./data"
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    SQLITE_URL: str = "sqlite:///./mina.db"
    
    # Supabase Configuration
    SUPABASE_DB_URL: Optional[str] = None  # Supabase PostgreSQL connection string
    SUPABASE_PROJECT_URL: Optional[str] = None  # Supabase project URL (optional)
    SUPABASE_ANON_KEY: Optional[str] = None  # Supabase anon key (optional)
    
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
    ENABLE_VIDEO_CALLS: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = False
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,doc,docx"

    @field_validator("DEBUG", "ENABLE_DOCS", mode="before")
    @classmethod
    def validate_boolean_flag(cls, v, info: ValidationInfo):
        if isinstance(v, bool):
            return v
        if v is None:
            return None if info.field_name == "ENABLE_DOCS" else False
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development", "dev", "local"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
                return False
        return v

    @field_validator("ALLOWED_EXTENSIONS")
    @classmethod
    def validate_extensions(cls, v):
        return [ext.strip().lower() for ext in v.split(",")]
    
    @property
    def database_url(self) -> str:
        """Return the appropriate database URL based on environment"""
        # Priority: SUPABASE_DB_URL > DATABASE_URL > SQLITE_URL
        return self.SUPABASE_DB_URL or self.DATABASE_URL or self.SQLITE_URL
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG

    @property
    def docs_enabled(self) -> bool:
        """Enable docs explicitly, or fall back to debug mode."""
        return self.DEBUG if self.ENABLE_DOCS is None else self.ENABLE_DOCS
    
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
