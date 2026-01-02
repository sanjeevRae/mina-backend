from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from typing import Generator

from app.config import settings

# Database Configuration
if settings.database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL/Supabase configuration
    # Optimized for Supabase free tier with SSL support
    connect_args = {}
    
    # Add SSL requirement for Supabase (and most cloud PostgreSQL)
    if "supabase" in settings.database_url or "amazonaws" in settings.database_url:
        connect_args["sslmode"] = "require"
    
    # Force IPv4 to avoid IPv6 unreachable errors
    # This is critical for networks that don't support IPv6
    db_url = settings.database_url
    if "supabase" in db_url and "@db." in db_url:
        # Replace db.xxx.supabase.co with aws-0-xxx.pooler.supabase.com (IPv4)
        # Or add connect_args to force IPv4 resolution
        import socket
        original_getaddrinfo = socket.getaddrinfo
        
        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        
        socket.getaddrinfo = getaddrinfo_ipv4_only
    
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        pool_size=5,  # Reduced for free tier memory optimization
        max_overflow=10,  # Reduced for free tier
        pool_recycle=300,  # Recycle connections every 5 minutes
        pool_pre_ping=True,  # Verify connections before using
        connect_args=connect_args,
        pool_timeout=10,  # Wait up to 10 seconds for connection
        execution_options={"isolation_level": "AUTOCOMMIT"}  # Better for serverless
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis connection
redis_client = None

def get_db() -> Generator[Session, None, None]:
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_redis():
    """Redis dependency"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            await redis_client.ping()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Redis connection failed: {e}. Continuing without Redis.")
            redis_client = None
    return redis_client


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)