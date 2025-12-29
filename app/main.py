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


# ======== SQLITE ENDPOINTS ========

@app.get("/sql-users-view")
async def sql_users_view():
    """View all users from SQLite database"""
    try:
        from app.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        users = db.query(User).all()
        
        user_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "phone": user.phone,
                "gender": user.gender,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
                "address": user.address,
                "emergency_contact": user.emergency_contact,
                "medical_conditions": user.medical_conditions or [],
                "allergies": user.allergies or [],
                "current_medications": user.current_medications or [],
                "created_at": str(user.created_at),
                "last_login": str(user.last_login) if user.last_login else None,
                "profile_image_url": user.profile_image_url
            }
            user_list.append(user_data)
        
        db.close()
        
        return {
            "total_users": len(user_list),
            "users": user_list,
            "storage": "SQLite Database"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "hint": "Check if User model exists in app.models.user"
        }

@app.get("/sql-tables")
async def sql_tables():
    """List all tables in SQLite database"""
    try:
        from app.database import engine
        
        with engine.connect() as conn:
            # For SQLite
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in result]
            
        return {
            "tables": tables,
            "database_type": "SQLite"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/sql-table/{table_name}")
async def sql_table_data(table_name: str):
    """View data from any table"""
    try:
        from app.database import engine
        
        with engine.connect() as conn:
            result = conn.execute(f"SELECT * FROM {table_name};")
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result]
            
        return {
            "table": table_name,
            "columns": list(columns),
            "row_count": len(rows),
            "data": rows[:100]  # Limit to 100 rows
        }
        
    except Exception as e:
        return {"error": str(e)}

# ======== END ========



# ======== REDIS ENDPOINTS ========
import redis
import json
import time
from datetime import datetime

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
        
        # Get sample values - FIXED FOR ALL DATA TYPES
        sample_data = {}
        for key in keys[:10]:  # First 10 keys
            try:
                key_type = redis_client.type(key)
                
                if key_type == "string":
                    value = redis_client.get(key)
                    if value:
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(value)
                            sample_data[key] = {"type": "string", "value": parsed}
                        except json.JSONDecodeError:
                            # If not JSON, use as string
                            sample_data[key] = {"type": "string", "value": str(value)[:200]}
                    else:
                        sample_data[key] = {"type": "string", "value": None}
                        
                elif key_type == "zset":  # This is your rate_limit key type!
                    # Get count and first few members
                    count = redis_client.zcard(key)
                    members = redis_client.zrange(key, 0, min(4, count-1), withscores=True)
                    
                    # Format members with readable timestamps
                    formatted_members = []
                    for member, score in members:
                        timestamp = datetime.fromtimestamp(score)
                        formatted_members.append({
                            "member": member,
                            "score": score,
                            "time": timestamp.isoformat(),
                            "age_seconds": int(time.time() - score)
                        })
                    
                    sample_data[key] = {
                        "type": "sorted_set",
                        "count": count,
                        "sample_members": formatted_members
                    }
                    
                elif key_type == "hash":
                    value = redis_client.hgetall(key)
                    sample_data[key] = {"type": "hash", "value": value}
                    
                elif key_type == "list":
                    length = redis_client.llen(key)
                    value = redis_client.lrange(key, 0, min(4, length-1))
                    sample_data[key] = {"type": "list", "count": length, "sample": value}
                    
                elif key_type == "set":
                    members = list(redis_client.smembers(key))
                    sample_data[key] = {"type": "set", "count": len(members), "sample": members[:5]}
                    
                else:
                    sample_data[key] = {"type": key_type, "info": "Unsupported type for display"}
                    
            except Exception as e:
                sample_data[key] = {"type": "error", "message": str(e)}
        
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

@app.get("/redis-users-explorer")
async def redis_users_explorer():
    """Find ALL user data in Redis - REAL USER DATA"""
    try:
        all_keys = redis_client.keys('*')
        
        # Find ALL keys that might contain user data
        user_related_keys = {
            "user_keys": [],
            "session_keys": [], 
            "auth_keys": [],
            "profile_keys": [],
            "login_keys": [],
            "token_keys": [],
            "email_keys": [],
            "password_keys": []
        }
        
        for key in all_keys:
            key_lower = key.lower()
            
            if 'user:' in key_lower:
                user_related_keys["user_keys"].append(key)
            elif 'session:' in key_lower:
                user_related_keys["session_keys"].append(key)
            elif 'auth:' in key_lower or 'login:' in key_lower:
                user_related_keys["auth_keys"].append(key)
            elif 'profile:' in key_lower:
                user_related_keys["profile_keys"].append(key)
            elif 'token:' in key_lower:
                user_related_keys["token_keys"].append(key)
            elif 'email:' in key_lower or '@' in key:
                user_related_keys["email_keys"].append(key)
            elif 'password:' in key_lower or 'pass:' in key_lower or 'pwd:' in key_lower:
                user_related_keys["password_keys"].append(key)
        
        # Get actual user data
        users_data = {}
        for key in user_related_keys["user_keys"]:
            try:
                key_type = redis_client.type(key)
                
                if key_type == "hash":
                    data = redis_client.hgetall(key)
                    users_data[key] = {"type": "hash", "data": data}
                elif key_type == "string":
                    data = redis_client.get(key)
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(data)
                        users_data[key] = {"type": "string", "data": parsed}
                    except:
                        users_data[key] = {"type": "string", "data": data}
                elif key_type == "zset":
                    data = redis_client.zrange(key, 0, -1, withscores=True)
                    users_data[key] = {"type": "sorted_set", "data": data}
            except Exception as e:
                users_data[key] = {"type": "error", "error": str(e)}
        
        # Get session data
        sessions_data = {}
        for key in user_related_keys["session_keys"][:20]:  # First 20
            try:
                data = redis_client.get(key)
                sessions_data[key] = data
            except:
                sessions_data[key] = "Error reading"
        
        # Get auth/login data
        auth_data = {}
        for key in user_related_keys["auth_keys"][:10]:
            try:
                key_type = redis_client.type(key)
                if key_type == "string":
                    auth_data[key] = redis_client.get(key)
                elif key_type == "hash":
                    auth_data[key] = redis_client.hgetall(key)
            except:
                auth_data[key] = "Error"
        
        return {
            "total_keys_in_redis": len(all_keys),
            "user_related_keys": user_related_keys,
            "users_count": len(user_related_keys["user_keys"]),
            "sessions_count": len(user_related_keys["session_keys"]),
            "auth_count": len(user_related_keys["auth_keys"]),
            "real_users_data": dict(list(users_data.items())[:20]),  # First 20 users
            "sample_sessions": sessions_data,
            "sample_auth_data": auth_data,
            "message": "This shows REAL user data from your Redis database"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/redis-raw-data")
async def redis_raw_data(pattern: str = "*"):
    """Get ALL raw data from Redis - COMPLETE DATA DUMP"""
    try:
        keys = redis_client.keys(pattern)
        
        all_data = {}
        for key in keys:
            try:
                key_type = redis_client.type(key)
                
                if key_type == "string":
                    value = redis_client.get(key)
                    all_data[key] = {
                        "type": "string",
                        "value": value,
                        "ttl": redis_client.ttl(key),
                        "size": len(str(value)) if value else 0
                    }
                    
                elif key_type == "hash":
                    value = redis_client.hgetall(key)
                    all_data[key] = {
                        "type": "hash", 
                        "value": value,
                        "ttl": redis_client.ttl(key),
                        "field_count": len(value)
                    }
                    
                elif key_type == "list":
                    value = redis_client.lrange(key, 0, -1)
                    all_data[key] = {
                        "type": "list",
                        "value": value,
                        "length": len(value),
                        "ttl": redis_client.ttl(key)
                    }
                    
                elif key_type == "set":
                    value = list(redis_client.smembers(key))
                    all_data[key] = {
                        "type": "set",
                        "value": value,
                        "count": len(value),
                        "ttl": redis_client.ttl(key)
                    }
                    
                elif key_type == "zset":
                    value = redis_client.zrange(key, 0, -1, withscores=True)
                    all_data[key] = {
                        "type": "zset",
                        "value": value,
                        "count": redis_client.zcard(key),
                        "ttl": redis_client.ttl(key)
                    }
                    
            except Exception as e:
                all_data[key] = {"error": str(e)}
        
        return {
            "pattern": pattern,
            "total_keys": len(keys),
            "data": all_data
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/redis-find-user/{search_term}")
async def redis_find_user(search_term: str):
    """Search for user data by email, username, or ID"""
    try:
        all_keys = redis_client.keys('*')
        results = []
        
        for key in all_keys:
            try:
                key_type = redis_client.type(key)
                
                if key_type == "hash":
                    data = redis_client.hgetall(key)
                    # Search in hash fields
                    for field, value in data.items():
                        if search_term.lower() in str(value).lower():
                            results.append({
                                "key": key,
                                "type": "hash",
                                "field": field,
                                "value": value,
                                "full_data": data
                            })
                
                elif key_type == "string":
                    value = redis_client.get(key)
                    if search_term.lower() in str(value).lower():
                        results.append({
                            "key": key,
                            "type": "string",
                            "value": value
                        })
                        
            except:
                continue
        
        return {
            "search_term": search_term,
            "results_count": len(results),
            "results": results[:50]  # Limit to 50 results
        }
        
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/redis-rate-limit-details")
async def redis_rate_limit_details():
    """View detailed rate limit information"""
    key = "rate_limit:202.166.207.163"
    
    try:
        if not redis_client.exists(key):
            return {"error": "Rate limit key not found"}
        
        # Get all members with scores
        all_members = redis_client.zrange(key, 0, -1, withscores=True)
        
        # Calculate statistics
        now = time.time()
        recent_cutoff = now - 3600  # Last hour
        
        recent_requests = []
        total_requests = len(all_members)
        
        for member, score in all_members:
            age = now - score
            if age <= 3600:  # Last hour
                recent_requests.append({
                    "timestamp": score,
                    "time": datetime.fromtimestamp(score).isoformat(),
                    "age_seconds": int(age)
                })
        
        # Sort by age
        recent_requests.sort(key=lambda x: x["age_seconds"])
        
        return {
            "key": key,
            "type": redis_client.type(key),
            "total_requests": total_requests,
            "recent_requests_last_hour": len(recent_requests),
            "requests": recent_requests[:20],  # First 20
            "ttl": redis_client.ttl(key),
            "description": "This is from your rate limiting middleware. Each request adds a timestamp."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ======== END ========


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