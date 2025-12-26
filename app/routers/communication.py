from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from database import get_db
from auth import get_current_user
from ..models.user import User, UserRole
from ..models.communication import ChatMessage, Notification
from schemas.communication import (
    ChatMessageCreate, ChatMessageResponse, ChatMessageMarkRead,
    NotificationCreate, NotificationResponse, NotificationMarkRead
)
from services.websocket_service import websocket_service

router = APIRouter(prefix="/communication", tags=["communication"])


@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message"""
    # Validate receiver exists
    receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    # Create message in database
    message = ChatMessage(
        **message_data.dict(),
        sender_id=current_user.id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Send via WebSocket if user is online
    await websocket_service.chat_manager.send_message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        message_content=message_data.content,
        message_type=message_data.message_type,
        appointment_id=message_data.appointment_id
    )
    
    # Build response
    response_data = ChatMessageResponse.from_orm(message)
    response_data.sender_name = current_user.full_name
    
    return response_data


@router.get("/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    conversation_with: int = Query(..., description="User ID to get conversation with"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    appointment_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a conversation"""
    query = db.query(ChatMessage).options(
        joinedload(ChatMessage.sender)
    ).filter(
        or_(
            and_(
                ChatMessage.sender_id == current_user.id,
                ChatMessage.receiver_id == conversation_with
            ),
            and_(
                ChatMessage.sender_id == conversation_with,
                ChatMessage.receiver_id == current_user.id
            )
        )
    )
    
    if appointment_id:
        query = query.filter(ChatMessage.appointment_id == appointment_id)
    
    # Order by creation time (newest first for pagination, but reverse for display)
    messages = query.order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    messages.reverse()  # Show oldest first in conversation
    
    # Mark messages as read
    unread_messages = [m for m in messages if m.receiver_id == current_user.id and not m.is_read]
    if unread_messages:
        message_ids = [m.id for m in unread_messages]
        db.query(ChatMessage).filter(ChatMessage.id.in_(message_ids)).update(
            {"is_read": True, "read_at": datetime.utcnow()},
            synchronize_session=False
        )
        db.commit()
    
    # Build response
    response_messages = []
    for message in messages:
        response_data = ChatMessageResponse.from_orm(message)
        response_data.sender_name = message.sender.full_name
        response_messages.append(response_data)
    
    return response_messages


@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of conversations for current user"""
    from sqlalchemy import func, case
    
    # Get latest message with each unique conversation partner
    subquery = db.query(
        case(
            (ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id),
            else_=ChatMessage.sender_id
        ).label('partner_id'),
        func.max(ChatMessage.created_at).label('last_message_time')
    ).filter(
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    ).group_by('partner_id').subquery()
    
    # Get the actual latest messages
    conversations = db.query(ChatMessage, User).join(
        subquery,
        and_(
            ChatMessage.created_at == subquery.c.last_message_time,
            or_(
                and_(
                    ChatMessage.sender_id == current_user.id,
                    ChatMessage.receiver_id == subquery.c.partner_id
                ),
                and_(
                    ChatMessage.receiver_id == current_user.id,
                    ChatMessage.sender_id == subquery.c.partner_id
                )
            )
        )
    ).join(
        User,
        User.id == subquery.c.partner_id
    ).order_by(ChatMessage.created_at.desc()).all()
    
    # Count unread messages for each conversation
    conversation_list = []
    for message, partner in conversations:
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.sender_id == partner.id,
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.is_read == False
        ).count()
        
        conversation_list.append({
            "partner_id": partner.id,
            "partner_name": partner.full_name,
            "partner_role": partner.role.value,
            "last_message": message.content,
            "last_message_time": message.created_at.isoformat(),
            "last_message_sender": message.sender_id,
            "unread_count": unread_count,
            "message_type": message.message_type
        })
    
    return conversation_list


@router.patch("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Message marked as read"}


@router.get("/typing/{user_id}")
async def send_typing_indicator(
    user_id: int,
    is_typing: bool = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Send typing indicator"""
    await websocket_service.chat_manager.typing_indicator(
        sender_id=current_user.id,
        receiver_id=user_id,
        is_typing=is_typing
    )
    
    return {"message": "Typing indicator sent"}


# Notifications endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_read: Optional[bool] = None,
    notification_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.patch("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update(
        {"is_read": True, "read_at": datetime.utcnow()},
        synchronize_session=False
    )
    db.commit()
    
    return {"message": "All notifications marked as read"}


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread messages and notifications"""
    unread_messages = db.query(ChatMessage).filter(
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False
    ).count()
    
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {
        "unread_messages": unread_messages,
        "unread_notifications": unread_notifications,
        "total_unread": unread_messages + unread_notifications
    }