import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError

from auth import verify_token
from services.websocket_service import websocket_service
from app.database import get_db
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_current_user_websocket(websocket: WebSocket, token: str = None) -> User:
    """Get current user from WebSocket token"""
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    
    try:
        payload = await verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        
        # Get user from database
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        
        return user
        
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """Main WebSocket endpoint for real-time communication"""
    user = await get_current_user_websocket(websocket, token)
    if not user:
        return
    
    # Connect user
    await websocket_service.connection_manager.connect(websocket, user.id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await websocket_service.handle_message(websocket, user.id, message)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }))
            except Exception as e:
                logger.error(f"Error handling message from user {user.id}: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "data": {"message": "Error processing message"}
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user.id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {str(e)}")
    finally:
        # Clean up connection
        websocket_service.connection_manager.disconnect(user.id)


@router.websocket("/ws/video/{room_id}/{token}")
async def video_call_websocket(websocket: WebSocket, room_id: str, token: str):
    """WebSocket endpoint specifically for video calls"""
    user = await get_current_user_websocket(websocket, token)
    if not user:
        return
    
    # Connect to WebSocket service
    await websocket_service.connection_manager.connect(websocket, user.id)
    
    # Join video call room
    join_result = await websocket_service.video_call_manager.join_video_call(room_id, user.id)
    
    if not join_result["success"]:
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": {"message": join_result["error"]}
        }))
        await websocket.close()
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle video call specific messages
                if message.get("type") in ["offer", "answer", "ice-candidate"]:
                    from app.schemas.communication import VideoCallSignal
                    signal = VideoCallSignal(
                        type=message["type"],
                        room_id=room_id,
                        user_id=user.id,
                        data=message.get("data")
                    )
                    await websocket_service.video_call_manager.handle_video_signal(signal)
                else:
                    await websocket_service.handle_message(websocket, user.id, message)
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }))
            except Exception as e:
                logger.error(f"Error in video call for user {user.id}: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Error processing video call message"}
                }))
    
    except WebSocketDisconnect:
        logger.info(f"Video call disconnected for user {user.id} in room {room_id}")
    except Exception as e:
        logger.error(f"Video call error for user {user.id}: {str(e)}")
    finally:
        # Leave room and clean up
        await websocket_service.video_call_manager.end_video_call(room_id, user.id)
        websocket_service.connection_manager.disconnect(user.id)


@router.get("/ws/test")
async def test_websocket_connection():
    """Test endpoint to check WebSocket service status"""
    active_connections = len(websocket_service.connection_manager.active_connections)
    active_rooms = len(websocket_service.connection_manager.room_connections)
    
    return {
        "status": "WebSocket service is running",
        "active_connections": active_connections,
        "active_video_rooms": active_rooms,
        "video_rooms": list(websocket_service.connection_manager.video_rooms.keys())
    }