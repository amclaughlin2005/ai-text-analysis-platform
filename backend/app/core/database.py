"""
Database configuration and session management for the AI-Powered Text Analysis Platform
Handles SQLAlchemy engine, session factory, and database connection management.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator
from .config import get_settings

# Get application settings
settings = get_settings()

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        poolclass=StaticPool,
        echo=settings.DEBUG  # Log SQL queries in debug mode
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=settings.DEBUG  # Log SQL queries in debug mode
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Used with FastAPI Depends() for automatic session management
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logging.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

async def get_db_async() -> Session:
    """
    Async version of get_db for WebSocket and background tasks
    Note: Returns regular session, not async. For true async, consider AsyncSession
    """
    return SessionLocal()

def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        # Import all models to ensure they're registered with Base
        from ..models import dataset, question, user, analytics, analysis_job
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Database tables initialized successfully")
        
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        raise

def drop_db():
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logging.info("🗑️  Database tables dropped successfully")
    except Exception as e:
        logging.error(f"❌ Database drop failed: {e}")
        raise

def reset_db():
    """
    Reset database by dropping and recreating all tables
    WARNING: This will delete all data!
    """
    drop_db()
    init_db()
    logging.info("🔄 Database reset completed")

class DatabaseHealthCheck:
    """Database health check utilities"""
    
    @staticmethod
    def check_connection() -> bool:
        """
        Check if database connection is healthy
        Returns True if connection is working, False otherwise
        """
        try:
            db = SessionLocal()
            # Simple query to test connection
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info() -> dict:
        """
        Get database connection information
        Returns dictionary with connection details
        """
        try:
            db = SessionLocal()
            
            # Get database name and version
            if settings.DATABASE_URL.startswith("sqlite"):
                result = db.execute("SELECT sqlite_version()").fetchone()
                db_type = "SQLite"
                db_version = result[0] if result else "Unknown"
            else:
                result = db.execute("SELECT version()").fetchone()
                db_type = "PostgreSQL"
                db_version = result[0].split()[1] if result else "Unknown"
            
            db.close()
            
            return {
                "type": db_type,
                "version": db_version,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "connection_healthy": True
            }
        except Exception as e:
            logging.error(f"Failed to get database info: {e}")
            return {
                "type": "Unknown",
                "version": "Unknown",
                "connection_healthy": False,
                "error": str(e)
            }

# Database utility functions
def create_database_url(
    user: str,
    password: str,
    host: str,
    port: int,
    database: str,
    driver: str = "postgresql"
) -> str:
    """
    Create database URL from components
    Useful for constructing connection strings programmatically
    """
    return f"{driver}://{user}:{password}@{host}:{port}/{database}"

def parse_database_url(url: str) -> dict:
    """
    Parse database URL into components
    Returns dictionary with connection details
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    return {
        "driver": parsed.scheme,
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path[1:] if parsed.path else None  # Remove leading slash
    }

# Transaction context manager
class DatabaseTransaction:
    """
    Context manager for database transactions
    Provides automatic commit/rollback handling
    """
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.should_close = session is None  # Only close if we created the session
    
    def __enter__(self) -> Session:
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
            logging.error(f"Transaction rolled back due to: {exc_val}")
        else:
            self.session.commit()
        
        if self.should_close:
            self.session.close()

# Export commonly used objects
__all__ = [
    'engine',
    'SessionLocal', 
    'Base',
    'get_db',
    'get_db_async',
    'init_db',
    'drop_db',
    'reset_db',
    'DatabaseHealthCheck',
    'DatabaseTransaction'
]
