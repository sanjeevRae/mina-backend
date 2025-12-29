from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from contextlib import asynccontextmanager
import sys
import os

from pathlib import Path

from app.config import settings
from app.database import init_db, engine, Base
from app.routers import auth
from app.routers import appointments
from app.routers import medical
from app.routers import ml_symptom_checker
from app.routers import communication
from app.routers import websocket

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Mina Backend...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create directories
    Path("./uploads").mkdir(exist_ok=True)
    Path("./models").mkdir(exist_ok=True)
    Path("./data/synthetic").mkdir(parents=True, exist_ok=True)
    Path("./archives").mkdir(exist_ok=True)
    
    # Start background tasks
    asyncio.create_task(start_background_tasks())
    
    logger.info("Mina Backend startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mina Backend...")


async def start_background_tasks():
    """Start background tasks"""
    from app.services.notification_service import notification_service
    
    # Start scheduled notification processor
    asyncio.create_task(process_scheduled_notifications())
    
    # Start ML model training scheduler (weekly retraining)
    asyncio.create_task(schedule_model_retraining())
    
    logger.info("Background tasks started")


async def process_scheduled_notifications():
    """Process scheduled notifications"""
    import asyncio
    from datetime import datetime
    from app.database import get_redis, get_db
    from app.models.communication import Notification
    import json
    
    while True:
        try:
            redis_client = await get_redis()
            now = datetime.utcnow().timestamp()
            
            # Get notifications that should be sent now
            scheduled = await redis_client.zrangebyscore(
                "scheduled_notifications", 
                0, 
                now, 
                withscores=True
            )
            
            for notification_data, score in scheduled:
                try:
                    data = json.loads(notification_data)
                    notification_id = data["id"]
                    
                    # Get notification from database
                    db = next(get_db())
                    notification = db.query(Notification).filter(
                        Notification.id == notification_id
                    ).first()
                    
                    if notification and not notification.is_sent:
                        from app.services.notification_service import notification_service
                        await notification_service.send_notification(notification)
                    
                    # Remove from scheduled set
                    await redis_client.zrem("scheduled_notifications", notification_data)
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled notification: {str(e)}")
            
            # Sleep for 60 seconds before checking again
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in notification scheduler: {str(e)}")
            await asyncio.sleep(300)  # Wait 5 minutes on error


async def schedule_model_retraining():
    """Schedule periodic model retraining"""
    import asyncio
    from datetime import datetime, timedelta
    from app.services.ml_service import get_symptom_checker_model
    from app.database import get_db
    from app.models.ml_models import MLModel
    
    while True:
        try:
            # Wait 7 days
            await asyncio.sleep(7 * 24 * 60 * 60)
            
            logger.info("Starting scheduled model retraining...")
            
            # Check if we have enough new feedback data
            db = next(get_db())
            recent_feedback_count = db.query(MLModel).filter(
                MLModel.created_at > datetime.utcnow() - timedelta(days=7)
            ).count()
            
            if recent_feedback_count > 100:  # Only retrain if we have enough new data
                ml_model = get_symptom_checker_model()
                training_metrics = ml_model.train(num_samples=15000)
                
                # Save new model
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = ml_model.save_model(version)
                
                # Deactivate old models
                db.query(MLModel).filter(
                    MLModel.model_name == "symptom_checker",
                    MLModel.is_active == True
                ).update({"is_active": False})
                
                # Save new model
                model_info = MLModel(
                    model_name="symptom_checker",
                    version=version,
                    file_path=model_path,
                    training_data_size=15000,
                    accuracy=training_metrics.get("condition_accuracy"),
                    precision=training_metrics.get("condition_precision"),
                    recall=training_metrics.get("condition_recall"),
                    f1_score=training_metrics.get("condition_f1"),
                    cross_validation_score=training_metrics.get("condition_cv_score"),
                    is_active=True
                )
                
                db.add(model_info)
                db.commit()
                
                logger.info(f"Model retrained successfully. New accuracy: {training_metrics.get('condition_accuracy', 0):.3f}")
            else:
                logger.info("Not enough new data for retraining, skipping this cycle")
                
        except Exception as e:
            logger.error(f"Error in model retraining: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Mina Backend",
    version=settings.VERSION,
    description="A comprehensive Mina backend built with FastAPI, featuring ML-powered symptom checking, video consultations, and complete medical record management - all running on free tier services.",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.render.com"]
    )

# ======== FIXED REDIS ENDPOINTS ========
import redis
import json

# Create Redis client with decode_responses=True
redis_client = redis.Redis.from_url(
    'rediss://red-d58fpluuk2gs73djegfg:PY5FJC6eNkCY6Vjiuj7dJ9jgUd4DjbyN@singapore-keyvalue.render.com:6379',
    decode_responses=True,  # THIS FIXES THE decode() ERROR!
    ssl_cert_reqs=None  # For SSL connection
)

@app.get("/redis-check")
async def redis_check():
    """Check Redis data - FIXED VERSION"""
    try:
        # Test connection
        redis_client.ping()
        
        # Get all keys
        keys = redis_client.keys('*')
        
        # Get sample values
        sample_data = {}
        for key in keys[:10]:  # First 10 keys
            try:
                value = redis_client.get(key)
                if value:
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(value)
                        sample_data[key] = parsed
                    except json.JSONDecodeError:
                        # If not JSON, use as string
                        sample_data[key] = str(value)[:200]  # First 200 chars
            except Exception as e:
                sample_data[key] = f"Error: {str(e)}"
        
        # Get Redis info
        redis_info = redis_client.info()
        
        return {
            "status": "success",
            "keys_count": len(keys),
            "keys": keys,
            "sample_data": sample_data,
            "redis_info": {
                "used_memory": redis_info.get('used_memory_human', 'N/A'),
                "connected_clients": redis_info.get('connected_clients', 'N/A'),
                "total_commands_processed": redis_info.get('total_commands_processed', 'N/A'),
                "uptime_in_seconds": redis_info.get('uptime_in_seconds', 'N/A')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/redis-view")
async def redis_view(key: str = ""):
    """View specific Redis key - FIXED"""
    try:
        if not key:
            return {"error": "No key provided. Use ?key=your_key"}
        
        # Check if key exists
        if not redis_client.exists(key):
            return {"error": f"Key '{key}' not found"}
        
        # Get key type
        key_type = redis_client.type(key)
        
        result = {"key": key, "type": key_type}
        
        if key_type == "string":
            value = redis_client.get(key)
            result["value"] = value
            result["length"] = len(value) if value else 0
            
        elif key_type == "hash":
            value = redis_client.hgetall(key)
            result["value"] = value
            
        elif key_type == "list":
            value = redis_client.lrange(key, 0, -1)
            result["value"] = value
            result["length"] = len(value)
            
        elif key_type == "set":
            value = redis_client.smembers(key)
            result["value"] = list(value)
            
        elif key_type == "zset":
            value = redis_client.zrange(key, 0, -1, withscores=True)
            result["value"] = value
            
        else:
            result["value"] = f"Unsupported type: {key_type}"
        
        # Get TTL
        ttl = redis_client.ttl(key)
        result["ttl"] = ttl if ttl > 0 else "no expiry"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/redis-command")
async def redis_command(cmd: str = ""):
    """Execute Redis command - FIXED"""
    try:
        if not cmd:
            return {"error": "No command provided. Use ?cmd=KEYS%20*"}
        
        # Parse command
        parts = cmd.strip().split()
        command = parts[0].upper()
        
        if command == "KEYS":
            pattern = parts[1] if len(parts) > 1 else "*"
            result = redis_client.keys(pattern)
            return {"result": result}
        
        elif command == "GET" and len(parts) > 1:
            key = parts[1]
            result = redis_client.get(key)
            return {"result": result}
        
        elif command == "SET" and len(parts) > 2:
            key = parts[1]
            value = ' '.join(parts[2:])
            result = redis_client.set(key, value)
            return {"result": "OK" if result else "Failed"}
        
        elif command == "DEL" and len(parts) > 1:
            keys = parts[1:]
            result = redis_client.delete(*keys)
            return {"result": f"Deleted {result} key(s)"}
        
        elif command == "DBSIZE":
            result = redis_client.dbsize()
            return {"result": result}
        
        elif command == "INFO":
            result = redis_client.info()
            return {"result": result}
        
        elif command == "TTL" and len(parts) > 1:
            key = parts[1]
            result = redis_client.ttl(key)
            return {"result": result}
        
        elif command == "EXPIRE" and len(parts) > 2:
            key = parts[1]
            seconds = int(parts[2])
            result = redis_client.expire(key, seconds)
            return {"result": "Set" if result else "Failed"}
        
        elif command == "FLUSHALL":
            return {"error": "FLUSHALL disabled for safety"}
        
        else:
            return {"error": f"Command '{command}' not supported"}
            
    except Exception as e:
        return {"error": str(e)}

@app.post("/redis-add-test")
async def add_test_data():
    """Add test data to Redis"""
    try:
        from datetime import datetime
        
        test_data = {
            "app:name": "Mina Backend",
            "app:version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "user:test:1": json.dumps({"name": "Test User", "email": "test@example.com"}),
            "cache:homepage": "Cached homepage data",
            "stats:visits": "100",
            "session:test": "active_session_123",
            "list:tasks": ["task1", "task2", "task3"],
            "hash:user:profile": {"name": "John", "age": "30"}
        }
        
        added = []
        
        # Add string values
        for key, value in test_data.items():
            if isinstance(value, (str, int, float)):
                redis_client.set(key, value)
                added.append(key)
            elif isinstance(value, list):
                redis_client.delete(key)  # Clear first
                for item in value:
                    redis_client.rpush(key, item)
                added.append(f"{key} (list)")
            elif isinstance(value, dict):
                redis_client.hset(key, mapping=value)
                added.append(f"{key} (hash)")
        
        return {
            "status": "success",
            "message": f"Added {len(added)} test items",
            "added": added
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/redis-clear-test")
async def clear_test_data():
    """Clear test data"""
    try:
        # Find test keys
        all_keys = redis_client.keys('*')
        test_keys = []
        
        for key in all_keys:
            if key.startswith(('app:', 'user:test:', 'cache:', 'stats:', 'session:', 'list:', 'hash:', 'test:')):
                test_keys.append(key)
        
        if test_keys:
            deleted = redis_client.delete(*test_keys)
            return {
                "status": "success",
                "message": f"Deleted {deleted} test keys",
                "deleted_keys": test_keys
            }
        else:
            return {
                "status": "success",
                "message": "No test keys found",
                "deleted_keys": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(medical.router, prefix="/api/v1")
app.include_router(ml_symptom_checker.router, prefix="/api/v1")
app.include_router(communication.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")

# Serve static files (uploaded files)
if Path("./uploads").exists():
    app.mount("/files", StaticFiles(directory="uploads"), name="files")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "database": "connected" if engine else "disconnected"
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Mina Backend API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
        "websocket": "/api/v1/ws/{token}",
        "features": [
            "JWT Authentication",
            "Appointment Management",
            "Medical Records",
            "Prescriptions",
            "AI Symptom Checker", 
            "Real-time Chat",
            "Video Consultations",
            "File Upload & Storage",
            "Email & Push Notifications"
        ]
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if not settings.DEBUG else str(exc)
        }
    )


# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Basic rate limiting middleware using Redis"""
    try:
        from app.database import get_redis
        import time
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/"] or request.url.path.startswith("/files"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        redis_client = await get_redis()
        
        # Rate limit key
        key = f"rate_limit:{client_ip}"
        current_time = int(time.time())
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        
        # Clean old entries and count requests
        await redis_client.zremrangebyscore(key, 0, window_start)
        request_count = await redis_client.zcard(key)
        
        if request_count >= settings.RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Add current request
        await redis_client.zadd(key, {str(current_time): current_time})
        await redis_client.expire(key, settings.RATE_LIMIT_WINDOW)
        
        return await call_next(request)
        
    except Exception as e:
        logger.warning(f"Rate limiting error: {str(e)}")
        return await call_next(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )