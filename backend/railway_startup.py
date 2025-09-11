#!/usr/bin/env python3
"""
Railway startup script that fixes database schema before starting the main app
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix database schema on Railway startup"""
    logger.info("🔧 Checking/fixing database schema...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ No DATABASE_URL found")
        return False
    
    try:
        engine = create_engine(database_url)
        
        # List of essential columns that might be missing
        essential_columns = [
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS original_filename VARCHAR(255)",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS csv_headers JSON",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS csv_delimiter VARCHAR(10) DEFAULT ','",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS csv_encoding VARCHAR(20) DEFAULT 'utf-8'",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS has_header_row BOOLEAN DEFAULT TRUE",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS total_questions INTEGER DEFAULT 0",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS processed_questions INTEGER DEFAULT 0",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS valid_questions INTEGER DEFAULT 0", 
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS invalid_questions INTEGER DEFAULT 0",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS organizations_count INTEGER DEFAULT 0",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS progress_percentage FLOAT DEFAULT 0.0",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS status_message TEXT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS sentiment_avg FLOAT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS avg_question_length FLOAT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS avg_response_length FLOAT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS avg_complexity_score FLOAT",
            "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS data_quality_score FLOAT"
        ]
        
        with engine.connect() as conn:
            # Check if datasets table exists first
            try:
                conn.execute(text("SELECT 1 FROM datasets LIMIT 1"))
                logger.info("✅ Datasets table exists")
            except:
                logger.info("📋 Creating datasets table...")
                create_table_sql = """
                CREATE TABLE datasets (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'processing',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                """
                conn.execute(text(create_table_sql))
                conn.commit()
            
            # Add missing columns
            for sql in essential_columns:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                except Exception as e:
                    # Ignore errors for columns that already exist
                    pass
            
            logger.info("✅ Database schema check completed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database schema fix failed: {e}")
        return False

if __name__ == "__main__":
    # Fix database schema
    fix_database_schema()
    
    # Then start the main application
    logger.info("🚀 Starting main application...")
    from railway_server import main
    main()
