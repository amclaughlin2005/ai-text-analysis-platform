#!/usr/bin/env python3
"""
Fix Railway database schema to match current models
This script will add missing columns and tables to Railway PostgreSQL
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Add the current directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Railway automatically provides DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback for local testing
        database_url = os.getenv("POSTGRES_URL", "postgresql://localhost/wordcloud")
    return database_url

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False

def add_missing_columns(engine):
    """Add missing columns to existing tables"""
    missing_columns = [
        # Core dataset columns that might be missing
        ("datasets", "description", "TEXT"),
        ("datasets", "original_filename", "VARCHAR(255)"),
        ("datasets", "csv_headers", "JSON"),
        ("datasets", "csv_delimiter", "VARCHAR(10) DEFAULT ','"),
        ("datasets", "csv_encoding", "VARCHAR(20) DEFAULT 'utf-8'"),
        ("datasets", "has_header_row", "BOOLEAN DEFAULT TRUE"),
        ("datasets", "total_questions", "INTEGER DEFAULT 0"),
        ("datasets", "processed_questions", "INTEGER DEFAULT 0"),
        ("datasets", "valid_questions", "INTEGER DEFAULT 0"),
        ("datasets", "invalid_questions", "INTEGER DEFAULT 0"),
        ("datasets", "processing_started_at", "TIMESTAMP"),
        ("datasets", "processing_completed_at", "TIMESTAMP"),
        ("datasets", "organizations_count", "INTEGER DEFAULT 0"),
        ("datasets", "is_public", "BOOLEAN DEFAULT FALSE"),
        
        # Progress tracking columns
        ("datasets", "progress_percentage", "FLOAT DEFAULT 0.0"),
        ("datasets", "status_message", "TEXT"),
        ("datasets", "sentiment_avg", "FLOAT"),
        ("datasets", "avg_question_length", "FLOAT"),
        ("datasets", "avg_response_length", "FLOAT"),
        ("datasets", "avg_complexity_score", "FLOAT"),
        ("datasets", "data_quality_score", "FLOAT"),
    ]
    
    with engine.connect() as conn:
        for table_name, column_name, column_type in missing_columns:
            if check_table_exists(engine, table_name):
                if not check_column_exists(engine, table_name, column_name):
                    try:
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                        logger.info(f"Adding column: {table_name}.{column_name}")
                        conn.execute(text(sql))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Failed to add column {table_name}.{column_name}: {e}")
                else:
                    logger.info(f"Column {table_name}.{column_name} already exists")
            else:
                logger.warning(f"Table {table_name} does not exist")

def create_minimal_schema(engine):
    """Create a minimal working schema if tables don't exist"""
    
    # Create datasets table with minimal columns
    create_datasets_sql = """
    CREATE TABLE IF NOT EXISTS datasets (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        file_path VARCHAR(500) NOT NULL,
        original_filename VARCHAR(255),
        file_size INTEGER NOT NULL,
        status VARCHAR(20) DEFAULT 'processing',
        progress_percentage FLOAT DEFAULT 0.0,
        status_message TEXT,
        total_questions INTEGER DEFAULT 0,
        processed_questions INTEGER DEFAULT 0,
        valid_questions INTEGER DEFAULT 0,
        invalid_questions INTEGER DEFAULT 0,
        sentiment_avg FLOAT,
        avg_question_length FLOAT,
        avg_response_length FLOAT,
        avg_complexity_score FLOAT,
        data_quality_score FLOAT,
        processing_started_at TIMESTAMP,
        processing_completed_at TIMESTAMP,
        csv_headers JSON,
        csv_delimiter VARCHAR(10) DEFAULT ',',
        csv_encoding VARCHAR(20) DEFAULT 'utf-8',
        has_header_row BOOLEAN DEFAULT TRUE,
        organizations_count INTEGER DEFAULT 0,
        is_public BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    with engine.connect() as conn:
        try:
            logger.info("Creating datasets table...")
            conn.execute(text(create_datasets_sql))
            conn.commit()
            logger.info("✅ Datasets table created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create datasets table: {e}")

def main():
    """Main function to fix Railway database schema"""
    logger.info("🔧 Starting Railway database schema fix...")
    
    # Get database URL
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ No database URL found in environment variables")
        return False
    
    logger.info(f"📊 Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Check if datasets table exists
        if check_table_exists(engine, "datasets"):
            logger.info("📋 Datasets table exists, adding missing columns...")
            add_missing_columns(engine)
        else:
            logger.info("📋 Datasets table does not exist, creating minimal schema...")
            create_minimal_schema(engine)
        
        logger.info("🎉 Database schema fix completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
