import json
import uuid
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from config import settings
from database import get_redis
from schemas.communication import WebSocketMessage, VideoCallSignal

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[int, WebSocket] = {}
        # Store connections by room ID for video calls
        self.room_connections: Dict[str, Set[int]] = {}
        # Store video call rooms
        self.video_rooms: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user"""
        await websocket.accept()
        
        # Disconnect existing connection if any
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
            except:
                pass
        
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
        
        # Notify user of successful connection
        await self.send_personal_message(user_id, {
            "type": "connection_established",
            "data": {"user_id": user_id, "timestamp": datetime.utcnow().isoformat()}
        })
    
    def disconnect(self, user_id: int):
        """Disconnect a user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from any video call rooms
        rooms_to_remove = []
        for room_id, users in self.room_connections.items():
            if user_id in users:
                users.remove(user_id)
                if len(users) == 0:
                    rooms_to_remove.append(room_id)
        
        for room_id in rooms_to_remove:
            del self.room_connections[room_id]
            if room_id in self.video_rooms:
                del self.video_rooms[room_id]
        
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, user_id: int, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                # Remove stale connection
                self.disconnect(user_id)
                return False
        return False
    
    async def send_message_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: Optional[int] = None):
        """Send message to all users in a room"""
        if room_id not in self.room_connections:
            return
        
        users = self.room_connections[room_id].copy()
        if exclude_user:
            users.discard(exclude_user)
        
        disconnected_users = []
        for user_id in users:
            success = await self.send_personal_message(user_id, message)
            if not success:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            if room_id in self.room_connections:
                self.room_connections[room_id].discard(user_id)
    
    async def join_room(self, room_id: str, user_id: int):
        """Add user to a room"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        
        self.room_connections[room_id].add(user_id)
        
        # Notify others in room
        await self.send_message_to_room(room_id, {
            "type": "user_joined",
            "data": {
                "room_id": room_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, exclude_user=user_id)
        
        logger.info(f"User {user_id} joined room {room_id}")
    
    async def leave_room(self, room_id: str, user_id: int):
        """Remove user from room"""
        if room_id in self.room_connections and user_id in self.room_connections[room_id]:
            self.room_connections[room_id].remove(user_id)
            
            # Notify others in room
            await self.send_message_to_room(room_id, {
                "type": "user_left",
                "data": {
                    "room_id": room_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            # Clean up empty room
            if len(self.room_connections[room_id]) == 0:
                del self.room_connections[room_id]
                if room_id in self.video_rooms:
                    del self.video_rooms[room_id]
        
        logger.info(f"User {user_id} left room {room_id}")
    
    def get_room_users(self, room_id: str) -> List[int]:
        """Get list of users in room"""
        return list(self.room_connections.get(room_id, set()))


class VideoCallManager:
    """Manage video call sessions"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def create_video_room(self, appointment_id: int, doctor_id: int, patient_id: int) -> str:
        """Create a new video call room"""
        room_id = f"video_{appointment_id}_{uuid.uuid4().hex[:8]}"
        
        room_data = {
            "room_id": room_id,
            "appointment_id": appointment_id,
            "participants": [doctor_id, patient_id],
            "created_at": datetime.utcnow().isoformat(),
            "status": "waiting"
        }
        
        self.connection_manager.video_rooms[room_id] = room_data
        
        # Notify participants
        for user_id in [doctor_id, patient_id]:
            await self.connection_manager.send_personal_message(user_id, {
                "type": "video_call_created",
                "data": {
                    "room_id": room_id,
                    "appointment_id": appointment_id,
                    "join_url": f"/video-call/{room_id}"
                }
            })
        
        logger.info(f"Created video room {room_id} for appointment {appointment_id}")
        return room_id
    
    async def join_video_call(self, room_id: str, user_id: int):
        """Join a video call"""
        if room_id not in self.connection_manager.video_rooms:
            return {"success": False, "error": "Room not found"}
        
        room_data = self.connection_manager.video_rooms[room_id]
        
        if user_id not in room_data["participants"]:
            return {"success": False, "error": "Not authorized to join this call"}
        
        await self.connection_manager.join_room(room_id, user_id)
        
        # Update room status
        room_data["status"] = "active"
        
        # Send room info to user
        await self.connection_manager.send_personal_message(user_id, {
            "type": "joined_video_call",
            "data": {
                "room_id": room_id,
                "participants": self.connection_manager.get_room_users(room_id),
                "room_data": room_data
            }
        })
        
        return {"success": True, "room_id": room_id}
    
    async def handle_video_signal(self, signal: VideoCallSignal):
        """Handle WebRTC signaling"""
        room_id = signal.room_id
        user_id = signal.user_id
        
        if room_id not in self.connection_manager.video_rooms:
            return {"success": False, "error": "Room not found"}
        
        # Forward signal to other participants
        message = {
            "type": "video_signal",
            "data": {
                "signal_type": signal.type,
                "from_user": user_id,
                "signal_data": signal.data
            }
        }
        
        await self.connection_manager.send_message_to_room(room_id, message, exclude_user=user_id)
        
        return {"success": True}
    
    async def end_video_call(self, room_id: str, user_id: int):
        """End a video call"""
        if room_id in self.connection_manager.video_rooms:
            room_data = self.connection_manager.video_rooms[room_id]
            room_data["status"] = "ended"
            room_data["ended_at"] = datetime.utcnow().isoformat()
            room_data["ended_by"] = user_id
            
            # Notify all participants
            await self.connection_manager.send_message_to_room(room_id, {
                "type": "video_call_ended",
                "data": {
                    "room_id": room_id,
                    "ended_by": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            # Clean up room connections
            if room_id in self.connection_manager.room_connections:
                users = list(self.connection_manager.room_connections[room_id])
                for participant_id in users:
                    await self.connection_manager.leave_room(room_id, participant_id)
        
        return {"success": True}


class ChatManager:
    """Manage chat messages"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def send_message(
        self, 
        sender_id: int, 
        receiver_id: int, 
        message_content: str,
        message_type: str = "text",
        appointment_id: Optional[int] = None
    ):
        """Send a chat message"""
        message = {
            "type": "chat_message",
            "data": {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": message_content,
                "message_type": message_type,
                "appointment_id": appointment_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Send to receiver
        success = await self.connection_manager.send_personal_message(receiver_id, message)
        
        # Send delivery confirmation to sender
        await self.connection_manager.send_personal_message(sender_id, {
            "type": "message_sent",
            "data": {
                "delivered": success,
                "receiver_id": receiver_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return success
    
    async def typing_indicator(self, sender_id: int, receiver_id: int, is_typing: bool):
        """Send typing indicator"""
        await self.connection_manager.send_personal_message(receiver_id, {
            "type": "typing_indicator",
            "data": {
                "sender_id": sender_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        })


class WebSocketService:
    """Main WebSocket service"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.video_call_manager = VideoCallManager(self.connection_manager)
        self.chat_manager = ChatManager(self.connection_manager)
    
    async def handle_message(self, websocket: WebSocket, user_id: int, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "chat_message":
                await self.chat_manager.send_message(
                    sender_id=user_id,
                    receiver_id=data.get("receiver_id"),
                    message_content=data.get("content"),
                    message_type=data.get("message_type", "text"),
                    appointment_id=data.get("appointment_id")
                )
            
            elif message_type == "typing":
                await self.chat_manager.typing_indicator(
                    sender_id=user_id,
                    receiver_id=data.get("receiver_id"),
                    is_typing=data.get("is_typing", False)
                )
            
            elif message_type == "join_video_call":
                result = await self.video_call_manager.join_video_call(
                    room_id=data.get("room_id"),
                    user_id=user_id
                )
                await self.connection_manager.send_personal_message(user_id, {
                    "type": "video_call_join_result",
                    "data": result
                })
            
            elif message_type == "video_signal":
                signal = VideoCallSignal(
                    type=data.get("signal_type"),
                    room_id=data.get("room_id"),
                    user_id=user_id,
                    data=data.get("signal_data")
                )
                await self.video_call_manager.handle_video_signal(signal)
            
            elif message_type == "end_video_call":
                result = await self.video_call_manager.end_video_call(
                    room_id=data.get("room_id"),
                    user_id=user_id
                )
                await self.connection_manager.send_personal_message(user_id, {
                    "type": "video_call_end_result",
                    "data": result
                })
            
            elif message_type == "ping":
                await self.connection_manager.send_personal_message(user_id, {
                    "type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {str(e)}")
            await self.connection_manager.send_personal_message(user_id, {
                "type": "error",
                "data": {"message": "Error processing message"}
            })
    
    async def send_notification(self, user_id: int, notification_data: Dict[str, Any]):
        """Send notification via WebSocket"""
        message = {
            "type": "notification",
            "data": notification_data
        }
        return await self.connection_manager.send_personal_message(user_id, message)


# Global WebSocket service instance
websocket_service = WebSocketService()