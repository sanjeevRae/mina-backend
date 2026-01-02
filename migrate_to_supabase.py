"""
Migrate existing SQLite data to Supabase PostgreSQL

This script helps you migrate data from your local SQLite database
to your new Supabase PostgreSQL database.

Usage:
    1. Set SUPABASE_DB_URL in .env file with your Supabase connection string
    2. Run: python migrate_to_supabase.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging

from app.config import settings
from app.database import Base
from app.models.user import User
from app.models.medical import MedicalRecord, HealthMetric
from app.models.appointment import Appointment
from app.models.communication import Message, Notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def migrate_data():
    """Migrate data from SQLite to Supabase PostgreSQL"""
    
    # Check if Supabase URL is configured
    supabase_url = settings.SUPABASE_DB_URL or settings.DATABASE_URL
    sqlite_url = settings.SQLITE_URL
    
    if not supabase_url or supabase_url.startswith("sqlite"):
        logger.error("❌ SUPABASE_DB_URL not configured!")
        logger.error("Please set SUPABASE_DB_URL in your .env file")
        logger.error("Example: SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres")
        return False
    
    # Check if SQLite database exists
    sqlite_path = sqlite_url.replace("sqlite:///", "")
    if not Path(sqlite_path).exists():
        logger.warning(f"⚠️  SQLite database not found at: {sqlite_path}")
        logger.info("Nothing to migrate. Starting with fresh Supabase database.")
        logger.info("Creating tables in Supabase...")
        
        # Just create tables in Supabase
        try:
            target_engine = create_engine(
                supabase_url,
                connect_args={"sslmode": "require"} if "supabase" in supabase_url else {},
                poolclass=NullPool
            )
            Base.metadata.create_all(bind=target_engine)
            logger.info("✅ Tables created successfully in Supabase!")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            return False
    
    logger.info("🚀 Starting migration from SQLite to Supabase...")
    logger.info(f"Source: {sqlite_url}")
    logger.info(f"Target: {supabase_url[:50]}...")
    
    try:
        # Create engines
        source_engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            poolclass=NullPool
        )
        
        target_engine = create_engine(
            supabase_url,
            connect_args={"sslmode": "require"} if "supabase" in supabase_url else {},
            poolclass=NullPool
        )
        
        # Create sessions
        SourceSession = sessionmaker(bind=source_engine)
        TargetSession = sessionmaker(bind=target_engine)
        
        source_session = SourceSession()
        target_session = TargetSession()
        
        # Create tables in target database
        logger.info("📋 Creating tables in Supabase...")
        Base.metadata.create_all(bind=target_engine)
        logger.info("✅ Tables created successfully!")
        
        # Get list of tables to migrate
        inspector = inspect(source_engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.warning("⚠️  No tables found in SQLite database")
            return True
        
        logger.info(f"📊 Found {len(tables)} tables to migrate: {', '.join(tables)}")
        
        # Models to migrate (in order due to foreign keys)
        models_to_migrate = [
            (User, "users"),
            (MedicalRecord, "medical_records"),
            (HealthMetric, "health_metrics"),
            (Appointment, "appointments"),
            (Message, "messages"),
            (Notification, "notifications")
        ]
        
        total_migrated = 0
        
        # Migrate each model
        for model, table_name in models_to_migrate:
            if table_name not in tables:
                logger.info(f"⏭️  Skipping {table_name} (not in source database)")
                continue
            
            try:
                # Get all records from source
                records = source_session.query(model).all()
                
                if not records:
                    logger.info(f"⏭️  {table_name}: No data to migrate")
                    continue
                
                logger.info(f"📦 Migrating {table_name}: {len(records)} records...")
                
                # Add records to target database
                for record in records:
                    # Create a new instance with the same data
                    record_dict = {
                        column.name: getattr(record, column.name)
                        for column in record.__table__.columns
                    }
                    new_record = model(**record_dict)
                    target_session.add(new_record)
                
                # Commit in batches
                target_session.commit()
                total_migrated += len(records)
                logger.info(f"✅ {table_name}: Migrated {len(records)} records")
                
            except Exception as e:
                logger.error(f"❌ Error migrating {table_name}: {e}")
                target_session.rollback()
                continue
        
        # Close sessions
        source_session.close()
        target_session.close()
        
        logger.info("=" * 60)
        logger.info(f"🎉 Migration completed successfully!")
        logger.info(f"📊 Total records migrated: {total_migrated}")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Update your Render environment variables:")
        logger.info("   DATABASE_URL = your_supabase_connection_string")
        logger.info("2. Deploy your application")
        logger.info("3. Test the connection")
        logger.info("")
        logger.info("Your data is now safely stored in Supabase! 🚀")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def verify_migration():
    """Verify that data was migrated successfully"""
    logger.info("🔍 Verifying migration...")
    
    supabase_url = settings.SUPABASE_DB_URL or settings.DATABASE_URL
    
    try:
        engine = create_engine(
            supabase_url,
            connect_args={"sslmode": "require"} if "supabase" in supabase_url else {},
            poolclass=NullPool
        )
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Count records in each table
        models = [
            (User, "Users"),
            (MedicalRecord, "Medical Records"),
            (HealthMetric, "Health Metrics"),
            (Appointment, "Appointments"),
            (Message, "Messages"),
            (Notification, "Notifications")
        ]
        
        logger.info("=" * 60)
        logger.info("📊 Supabase Database Contents:")
        logger.info("=" * 60)
        
        for model, name in models:
            try:
                count = session.query(model).count()
                logger.info(f"{name}: {count} records")
            except Exception as e:
                logger.warning(f"{name}: Unable to count ({str(e)[:50]})")
        
        session.close()
        logger.info("=" * 60)
        logger.info("✅ Verification complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False


def main():
    """Main migration script"""
    print("=" * 60)
    print("🗄️  Supabase Migration Tool")
    print("=" * 60)
    print("")
    
    # Perform migration
    success = migrate_data()
    
    if success:
        print("")
        # Verify migration
        verify_migration()
    else:
        print("")
        print("❌ Migration failed. Please check the logs above.")
        print("")
        print("Common issues:")
        print("1. SUPABASE_DB_URL not set in .env file")
        print("2. Invalid connection string")
        print("3. Network connectivity issues")
        print("4. Database permissions")
        print("")
        sys.exit(1)


if __name__ == "__main__":
    main()
