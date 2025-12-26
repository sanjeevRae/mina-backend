import smtplib
import json
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import redis.asyncio as redis

from config import settings
from database import get_db, get_redis
from models.communication import Notification
from schemas.communication import NotificationCreate

logger = logging.getLogger(__name__)


class EmailService:
    """Handle email notifications using EmailJS and fallback SMTP"""
    
    def __init__(self):
        self.emailjs_service_id = settings.EMAILJS_SERVICE_ID
        self.emailjs_template_id = settings.EMAILJS_TEMPLATE_ID
        self.emailjs_public_key = settings.EMAILJS_PUBLIC_KEY
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str, 
        template_params: Optional[Dict] = None
    ) -> bool:
        """Send email using EmailJS service"""
        try:
            if not all([self.emailjs_service_id, self.emailjs_template_id, self.emailjs_public_key]):
                logger.warning("EmailJS credentials not configured")
                return False
            
            # Prepare EmailJS payload
            payload = {
                "service_id": self.emailjs_service_id,
                "template_id": self.emailjs_template_id,
                "user_id": self.emailjs_public_key,
                "template_params": {
                    "to_email": to_email,
                    "subject": subject,
                    "message": content,
                    **(template_params or {})
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.emailjs.com/api/v1.0/email/send",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"Failed to send email: {response.status_code} {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False


class PushNotificationService:
    """Handle push notifications using Firebase"""
    
    def __init__(self):
        self.firebase_project_id = settings.FIREBASE_PROJECT_ID
        self.service_account = settings.firebase_service_account
    
    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Send push notification via Firebase FCM HTTP v1 API"""
        try:
            if not (self.firebase_project_id and self.service_account):
                logger.warning("Firebase service account not configured")
                return False

            import aiohttp
            import google.auth
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account

            # Get access token from service account
            credentials = service_account.IDTokenCredentials.from_service_account_info(
                self.service_account,
                target_audience="https://firebase.googleapis.com/"
            )
            credentials.refresh(Request())
            access_token = credentials.token

            url = f"https://fcm.googleapis.com/v1/projects/{self.firebase_project_id}/messages:send"
            payload = {
                "message": {
                    "token": device_token,
                    "notification": {
                        "title": title,
                        "body": body
                    },
                    "data": data or {}
                }
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; UTF-8"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        logger.info(f"Push notification sent: {title}")
                        return True
                    else:
                        logger.error(f"Failed to send push notification: {resp.status} {await resp.text()}")
                        return False
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False


class NotificationService:
    """Centralized notification service"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.push_service = PushNotificationService()
    
    async def create_notification(
        self, 
        notification_data: NotificationCreate,
        db_session = None
    ) -> Notification:
        """Create a notification in the database"""
        if db_session is None:
            db_session = next(get_db())
        
        notification = Notification(**notification_data.dict())
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)
        
        # Schedule delivery if needed
        if notification.scheduled_at and notification.scheduled_at > datetime.utcnow():
            await self._schedule_notification(notification)
        else:
            await self.send_notification(notification)
        
        return notification
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send a notification via all requested channels"""
        success = True
        
        try:
            # Get user info (you'd fetch this from the database)
            # user = db.query(User).filter(User.id == notification.user_id).first()
            
            # Send email if requested
            if notification.send_email:
                email_sent = await self.email_service.send_email(
                    to_email="user@example.com",  # Replace with actual user email
                    subject=notification.title,
                    content=notification.message
                )
                success = success and email_sent
            
            # Send push notification if requested
            if notification.send_push:
                push_sent = await self.push_service.send_push_notification(
                    device_token="device_token",  # Replace with actual device token
                    title=notification.title,
                    body=notification.message
                )
                success = success and push_sent
            
            # Update notification status
            if success:
                notification.is_sent = True
                notification.sent_at = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
            success = False
        
        return success
    
    async def _schedule_notification(self, notification: Notification):
        """Schedule a notification for later delivery"""
        redis_client = await get_redis()
        
        # Store notification for scheduled delivery
        notification_data = {
            "id": notification.id,
            "scheduled_at": notification.scheduled_at.isoformat()
        }
        
        await redis_client.zadd(
            "scheduled_notifications",
            {json.dumps(notification_data): notification.scheduled_at.timestamp()}
        )
    
    async def send_appointment_reminder(
        self, 
        user_id: int, 
        appointment_id: int, 
        appointment_time: datetime,
        hours_before: int = 24
    ):
        """Send appointment reminder notification"""
        reminder_time = appointment_time - timedelta(hours=hours_before)
        
        notification = NotificationCreate(
            user_id=user_id,
            title="Appointment Reminder",
            message=f"You have an appointment scheduled for {appointment_time.strftime('%B %d, %Y at %I:%M %p')}",
            notification_type="appointment_reminder",
            related_appointment_id=appointment_id,
            scheduled_at=reminder_time,
            send_email=True,
            send_push=True
        )
        
        return await self.create_notification(notification)
    
    async def send_prescription_notification(
        self, 
        user_id: int, 
        prescription_id: int, 
        medication_name: str
    ):
        """Send new prescription notification"""
        notification = NotificationCreate(
            user_id=user_id,
            title="New Prescription",
            message=f"You have a new prescription for {medication_name}. Please review the details.",
            notification_type="new_prescription",
            related_prescription_id=prescription_id,
            send_email=True,
            send_push=True
        )
        
        return await self.create_notification(notification)
    
    async def send_test_results_notification(
        self, 
        user_id: int, 
        test_name: str
    ):
        """Send test results available notification"""
        notification = NotificationCreate(
            user_id=user_id,
            title="Test Results Available",
            message=f"Your {test_name} results are now available. Please log in to view them.",
            notification_type="test_results",
            send_email=True,
            send_push=True
        )
        
        return await self.create_notification(notification)


# Global notification service instance
notification_service = NotificationService()