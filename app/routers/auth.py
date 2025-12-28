from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import create_access_token, create_refresh_token, verify_password, get_password_hash, verify_token, blacklist_token, get_current_user
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, TokenRefresh, 
    PasswordChange, PasswordReset, PasswordResetConfirm, UserUpdate
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    
    new_user = User(
        **user_dict,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens"""
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token"""
    payload = await verify_token(token_data.refresh_token, "refresh")
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Blacklist old refresh token
    exp = payload.get("exp")
    if exp:
        expiry_time = exp - int(datetime.utcnow().timestamp())
        await blacklist_token(token_data.refresh_token, expiry_time)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials = Depends(security)
):
    """Logout user and blacklist token"""
    token = credentials.credentials
    
    # Calculate token expiry time
    payload = await verify_token(token)
    exp = payload.get("exp")
    expiry_time = exp - int(datetime.utcnow().timestamp())
    
    # Blacklist token
    await blacklist_token(token, expiry_time)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    user = db.query(User).filter(User.email == password_reset.email).first()
    
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    # In production, you would:
    # 1. Generate a secure reset token
    # 2. Store it in database with expiry
    # 3. Send email with reset link
    # 4. Handle the reset confirmation
    
    # For now, simulate sending email
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset"""
    # In production, you would:
    # 1. Verify the reset token
    # 2. Check if it's not expired
    # 3. Update the user's password
    # 4. Delete the reset token
    
    # For now, simulate the process
    return {"message": "Password reset successfully"}


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List users (admin or for finding doctors)"""
    query = db.query(User)
    
    # Filter by role if specified
    if role:
        query = query.filter(User.role == role)
    
    # If current user is not admin, only show active users and limit fields
    if current_user.role != UserRole.ADMIN:
        query = query.filter(User.is_active == True)
    
    users = query.offset(skip).limit(limit).all()
    return users