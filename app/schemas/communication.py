from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    appointment_id: Optional[int] = None
    receiver_id: int
    message_type: str = "text"
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    sender_id: int
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime
    
    # Include sender info
    sender_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatMessageMarkRead(BaseModel):
    message_id: int


class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: str
    related_appointment_id: Optional[int] = None
    related_prescription_id: Optional[int] = None
    send_email: bool = True
    send_push: bool = True
    send_sms: bool = False
    scheduled_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    is_read: bool = False
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    notification_id: int


class WebSocketMessage(BaseModel):
    type: str  # message, notification, video_call, etc.
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None


class VideoCallSignal(BaseModel):
    type: str  # offer, answer, ice-candidate, join, leave
    room_id: str
    user_id: int
    data: Optional[Dict[str, Any]] = None