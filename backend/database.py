"""
Database configuration and session management for the AI Text Analysis Platform
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wordcloud_analysis.db")

# For SQLite (development), we need special configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,  # Allow multiple threads for SQLite
            "timeout": 20,
        },
        echo=False  # Set to True for SQL debugging
    )
else:
    # For PostgreSQL in production (Railway)
    engine = create_engine(
        DATABASE_URL,
        # Production optimizations
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        echo=False  # Set to True for SQL debugging
    )

# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency injection for FastAPI
def get_db() -> Session:
    """
    Create and yield a database session.
    This will be used as a dependency in FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        logger.info("📊 Database session created")
        yield db
    except Exception as e:
        logger.error(f"❌ Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.info("🔐 Database session closed")

def create_all_tables():
    """
    Create all database tables based on the defined models.
    Run this on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def check_database_connection():
    """
    Verify database connectivity
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).fetchone()
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Export database utilities
__all__ = [
    'engine',
    'SessionLocal', 
    'Base',
    'get_db',
    'create_all_tables',
    'check_database_connection'
]
