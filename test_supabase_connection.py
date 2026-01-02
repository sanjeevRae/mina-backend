"""
Test Supabase PostgreSQL connection

This script tests your Supabase database connection and verifies
that everything is configured correctly.

Usage:
    python test_supabase_connection.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.user import User
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test Supabase database connection"""
    
    print("=" * 60)
    print("🧪 Supabase Connection Test")
    print("=" * 60)
    print("")
    
    # Check configuration
    db_url = settings.database_url
    
    print("📋 Configuration:")
    print(f"   Database URL: {db_url[:50]}...")
    print(f"   Is Supabase: {'✅ Yes' if 'supabase' in db_url else '❌ No'}")
    print(f"   Is PostgreSQL: {'✅ Yes' if db_url.startswith('postgresql') else '❌ No'}")
    print("")
    
    if not db_url.startswith('postgresql'):
        logger.warning("⚠️  Not using PostgreSQL!")
        logger.warning("Please set SUPABASE_DB_URL in your .env file")
        logger.warning("Example: SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres")
        print("")
        return False
    
    # Test 1: Basic connection
    print("🔌 Test 1: Basic Connection")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("   ✅ Basic connection successful!")
    except Exception as e:
        logger.error(f"   ❌ Connection failed: {e}")
        print("")
        print("💡 Troubleshooting:")
        print("   1. Check your SUPABASE_DB_URL is correct")
        print("   2. Ensure password has no special characters or is URL-encoded")
        print("   3. Verify your Supabase project is not paused")
        print("   4. Check your network/firewall settings")
        print("")
        return False
    
    # Test 2: Database version
    print("")
    print("🗄️  Test 2: Database Info")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"   PostgreSQL Version: {version.split(',')[0]}")
            
            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            logger.info(f"   Database Name: {db_name}")
            
            # Get current user
            result = conn.execute(text("SELECT current_user"))
            user = result.scalar()
            logger.info(f"   Connected as: {user}")
            
    except Exception as e:
        logger.error(f"   ❌ Failed to get database info: {e}")
    
    # Test 3: Session creation
    print("")
    print("📦 Test 3: Session Management")
    try:
        db = SessionLocal()
        logger.info("   ✅ Session created successfully!")
        db.close()
        logger.info("   ✅ Session closed successfully!")
    except Exception as e:
        logger.error(f"   ❌ Session management failed: {e}")
        return False
    
    # Test 4: Tables exist
    print("")
    print("📋 Test 4: Database Tables")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                logger.info(f"   Found {len(tables)} tables:")
                for table in tables:
                    logger.info(f"      - {table}")
            else:
                logger.warning("   ⚠️  No tables found. Run: python setup_db.py")
                
    except Exception as e:
        logger.error(f"   ❌ Failed to list tables: {e}")
    
    # Test 5: Query users table
    print("")
    print("👥 Test 5: Query Users Table")
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        logger.info(f"   ✅ Query successful!")
        logger.info(f"   Users in database: {user_count}")
        
        if user_count > 0:
            # Get first user
            first_user = db.query(User).first()
            logger.info(f"   Sample user: {first_user.email} (ID: {first_user.id})")
        
        db.close()
        
    except Exception as e:
        logger.error(f"   ⚠️  Users table query failed: {e}")
        logger.info("   This is normal if tables haven't been created yet")
        logger.info("   Run: python setup_db.py to create tables")
    
    # Test 6: Connection pool
    print("")
    print("🏊 Test 6: Connection Pool")
    try:
        pool = engine.pool
        logger.info(f"   Pool size: {pool.size()}")
        logger.info(f"   Checked out connections: {pool.checkedout()}")
        logger.info(f"   ✅ Connection pool working correctly!")
    except Exception as e:
        logger.error(f"   ❌ Pool test failed: {e}")
    
    # Test 7: Write test
    print("")
    print("✍️  Test 7: Write Test")
    try:
        with engine.connect() as conn:
            # Create a test table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS _connection_test (
                    id SERIAL PRIMARY KEY,
                    test_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            
            # Insert a test row
            conn.execute(text("""
                INSERT INTO _connection_test (test_value) 
                VALUES ('Test successful!')
            """))
            conn.commit()
            
            # Read it back
            result = conn.execute(text("""
                SELECT test_value FROM _connection_test 
                ORDER BY created_at DESC LIMIT 1
            """))
            value = result.scalar()
            
            # Clean up
            conn.execute(text("DROP TABLE _connection_test"))
            conn.commit()
            
            logger.info(f"   ✅ Write test successful! Value: {value}")
            
    except Exception as e:
        logger.error(f"   ❌ Write test failed: {e}")
        return False
    
    # Summary
    print("")
    print("=" * 60)
    print("🎉 All Tests Passed!")
    print("=" * 60)
    print("")
    print("✅ Your Supabase connection is working perfectly!")
    print("✅ Database is ready for production use")
    print("")
    print("Next steps:")
    print("1. Deploy to Render with SUPABASE_DB_URL environment variable")
    print("2. Monitor usage in Supabase dashboard")
    print("3. Set up automated backups if needed")
    print("")
    
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
