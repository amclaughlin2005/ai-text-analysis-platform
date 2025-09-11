#!/usr/bin/env python3
"""
Inspect Railway database schema and provide a comprehensive fix
This will show us exactly what columns exist vs what we expect
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_railway_schema():
    """Inspect the actual Railway database schema"""
    logger.info("🔍 Inspecting Railway database schema...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ No DATABASE_URL found")
        return False
    
    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Get all tables
        tables = inspector.get_table_names()
        logger.info(f"📋 Found tables: {tables}")
        
        # Focus on datasets table
        if 'datasets' in tables:
            columns = inspector.get_columns('datasets')
            logger.info(f"📊 Datasets table has {len(columns)} columns:")
            
            for col in columns:
                logger.info(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
                
            # Show which columns we expect but don't have
            expected_columns = [
                'id', 'name', 'description', 'file_path', 'original_filename', 
                'filename', 'file_size', 'total_rows', 'status', 'progress_percentage',
                'status_message', 'total_questions', 'processed_questions', 
                'valid_questions', 'invalid_questions', 'created_at', 'updated_at'
            ]
            
            existing_columns = [col['name'] for col in columns]
            missing_columns = [col for col in expected_columns if col not in existing_columns]
            extra_columns = [col for col in existing_columns if col not in expected_columns]
            
            if missing_columns:
                logger.warning(f"❌ Missing expected columns: {missing_columns}")
            
            if extra_columns:
                logger.info(f"➕ Extra columns in Railway: {extra_columns}")
                
            return {
                'existing_columns': existing_columns,
                'missing_columns': missing_columns,
                'extra_columns': extra_columns,
                'all_columns': columns
            }
        else:
            logger.error("❌ Datasets table not found!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to inspect schema: {e}")
        return False

if __name__ == "__main__":
    result = inspect_railway_schema()
    if result:
        print("\n" + "="*50)
        print("RAILWAY SCHEMA INSPECTION COMPLETE")
        print("="*50)
        print(f"Existing columns: {len(result['existing_columns'])}")
        print(f"Missing columns: {len(result['missing_columns'])}")
        print(f"Extra columns: {len(result['extra_columns'])}")
    else:
        print("Failed to inspect Railway schema")
        sys.exit(1)
