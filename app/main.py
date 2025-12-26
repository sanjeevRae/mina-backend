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
    logger.info("Starting Telemedicine Backend...")
    
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
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telemedicine Backend...")


async def start_background_tasks():
    """Start background tasks"""
    from services.notification_service import notification_service
    
    # Start scheduled notification processor
    asyncio.create_task(process_scheduled_notifications())
    
    # Start ML model training scheduler (weekly retraining)
    asyncio.create_task(schedule_model_retraining())
    
    logger.info("Background tasks started")


async def process_scheduled_notifications():
    """Process scheduled notifications"""
    import asyncio
    from datetime import datetime
    from database import get_redis, get_db
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
                        from services.notification_service import notification_service
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
    from services.ml_service import get_symptom_checker_model
    from database import get_db
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
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A comprehensive telemedicine backend built with FastAPI, featuring ML-powered symptom checking, video consultations, and complete medical record management - all running on free tier services.",
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
        "message": "Telemedicine Backend API",
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
        from database import get_redis
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