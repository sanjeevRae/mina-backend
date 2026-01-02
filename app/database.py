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
    connect_args = {"sslmode": "require"}
    
    # Force IPv4 connection by modifying psycopg2 connection parameters
    # This prevents "Network is unreachable" errors on IPv6-only DNS responses
    db_url = settings.database_url
    
    # Extract host from connection string and force IPv4 resolution
    if "supabase" in db_url:
        import socket
        import re
        
        # Parse the hostname from connection string
        match = re.search(r'@([^:]+):', db_url)
        if match:
            hostname = match.group(1)
            try:
                # Try to get IPv4 address explicitly
                ipv4_addr = None
                for addr_info in socket.getaddrinfo(hostname, None, socket.AF_INET):
                    ipv4_addr = addr_info[4][0]
                    break
                
                # If we got an IPv4 address, replace hostname in connection string
                if ipv4_addr:
                    db_url = db_url.replace(f'@{hostname}:', f'@{ipv4_addr}:')
                    # Add host parameter to force hostname for SSL verification
                    connect_args["host"] = ipv4_addr
                    connect_args["hostaddr"] = ipv4_addr
                    import logging
                    logging.info(f"Supabase connection using IPv4: {ipv4_addr}")
            except socket.gaierror:
                # If IPv4 resolution fails, try to continue with original
                import logging
                logging.warning(f"Could not resolve IPv4 for {hostname}, using original URL")
                pass
    
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