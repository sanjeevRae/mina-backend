from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    message_type = Column(String(20), default="text")  # text, image, file, system
    content = Column(Text, nullable=False)
    file_url = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id})>"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # appointment, prescription, system, etc.
    
    # Related entity IDs
    related_appointment_id = Column(Integer, ForeignKey("appointments.id"))
    related_prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Delivery methods
    send_email = Column(Boolean, default=True)
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}')>"