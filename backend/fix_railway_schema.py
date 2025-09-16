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
        
        # CRITICAL: Questions table metadata columns for filtering
        ("questions", "org_name", "VARCHAR(255)"),
        ("questions", "org_id", "VARCHAR(255)"),
        ("questions", "user_id_from_csv", "VARCHAR(255)"),
        ("questions", "timestamp_from_csv", "TIMESTAMP"),
        ("questions", "context", "TEXT"),
        ("questions", "is_valid", "BOOLEAN DEFAULT TRUE"),
        ("questions", "validation_errors", "JSON"),
        ("questions", "data_quality_score", "FLOAT"),
        ("questions", "question_length", "INTEGER"),
        ("questions", "response_length", "INTEGER"),
        ("questions", "context_length", "INTEGER"),
        ("questions", "word_count_question", "INTEGER"),
        ("questions", "word_count_response", "INTEGER"),
        ("questions", "sentiment_score", "FLOAT"),
        ("questions", "sentiment_label", "VARCHAR(20)"),
        ("questions", "sentiment_confidence", "FLOAT"),
        ("questions", "question_type", "VARCHAR(50)"),
        ("questions", "question_intent", "VARCHAR(50)"),
        ("questions", "complexity_score", "FLOAT"),
        ("questions", "urgency_level", "VARCHAR(20)"),
        ("questions", "response_relevance_score", "FLOAT"),
        ("questions", "response_completeness_score", "FLOAT"),
        ("questions", "response_quality_score", "FLOAT"),
        ("questions", "query_response_similarity", "FLOAT"),
        ("questions", "readability_question", "FLOAT"),
        ("questions", "readability_response", "FLOAT"),
        ("questions", "processed_at", "TIMESTAMP"),
        ("questions", "processing_version", "VARCHAR(20)"),
        ("questions", "requires_reprocessing", "BOOLEAN DEFAULT FALSE"),
        ("questions", "csv_source_info", "JSON"),
        ("questions", "updated_at", "TIMESTAMP DEFAULT NOW()"),
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

def populate_metadata_from_csv(engine, dataset_id="f4f5cff7-7fae-403c-af63-5ed92908532d"):
    """Populate metadata columns from the original CSV file"""
    import csv
    import io
    from datetime import datetime
    
    csv_file_path = f"uploads/{dataset_id}_CWYC-71k-155k.csv"
    
    try:
        # Check if CSV file exists
        if not os.path.exists(csv_file_path):
            logger.warning(f"CSV file not found: {csv_file_path}")
            return False
            
        logger.info(f"📄 Reading CSV file: {csv_file_path}")
        
        # Read CSV and map data
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Read first line to get headers
            content = file.read()
            csv_reader = csv.reader(io.StringIO(content))
            headers = next(csv_reader, [])
            
            # Strip BOM from first header if present
            if headers and headers[0].startswith('\ufeff'):
                headers[0] = headers[0][1:]
            
            logger.info(f"📋 CSV Headers: {headers}")
            
            # Find column indices
            org_name_idx = None
            user_email_idx = None
            timestamp_idx = None
            
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if header_lower in ['orgname', 'org_name']:
                    org_name_idx = i
                elif header_lower in ['user_email', 'useremail']:
                    user_email_idx = i
                elif header_lower in ['timestamp']:
                    timestamp_idx = i
            
            logger.info(f"🔍 Found columns - org_name: {org_name_idx}, user_email: {user_email_idx}, timestamp: {timestamp_idx}")
            
            if org_name_idx is None and user_email_idx is None:
                logger.warning("No metadata columns found in CSV")
                return False
            
            # Reset reader and process rows
            csv_reader = csv.reader(io.StringIO(content))
            next(csv_reader)  # Skip headers
            
            with engine.connect() as conn:
                # Get existing questions in row order
                questions_sql = text("""
                    SELECT id, csv_row_number, original_question 
                    FROM questions 
                    WHERE dataset_id = :dataset_id 
                    ORDER BY csv_row_number
                """)
                questions = conn.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
                
                logger.info(f"📊 Found {len(questions)} questions to update")
                
                # Create a mapping from row numbers to question IDs
                row_to_question = {}
                for q in questions:
                    if q.csv_row_number:
                        row_to_question[q.csv_row_number] = q.id
                
                # Process CSV rows and update database
                update_count = 0
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because header is row 1
                    if row_num in row_to_question:
                        question_id = row_to_question[row_num]
                        
                        # Extract metadata
                        org_name = row[org_name_idx] if org_name_idx is not None and len(row) > org_name_idx else None
                        user_email = row[user_email_idx] if user_email_idx is not None and len(row) > user_email_idx else None
                        timestamp_str = row[timestamp_idx] if timestamp_idx is not None and len(row) > timestamp_idx else None
                        
                        # Parse timestamp
                        timestamp_parsed = None
                        if timestamp_str:
                            try:
                                # Try common timestamp formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%Y %H:%M:%S']:
                                    try:
                                        timestamp_parsed = datetime.strptime(timestamp_str, fmt)
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass
                        
                        # Update the question
                        update_sql = text("""
                            UPDATE questions 
                            SET org_name = :org_name,
                                user_id_from_csv = :user_email,
                                timestamp_from_csv = :timestamp
                            WHERE id = :question_id
                        """)
                        
                        conn.execute(update_sql, {
                            "question_id": question_id,
                            "org_name": org_name,
                            "user_email": user_email,
                            "timestamp": timestamp_parsed
                        })
                        
                        update_count += 1
                        
                        if update_count % 1000 == 0:
                            logger.info(f"📊 Updated {update_count} questions...")
                
                conn.commit()
                logger.info(f"✅ Successfully updated {update_count} questions with metadata")
                return True
                
    except Exception as e:
        logger.error(f"❌ Failed to populate metadata: {e}")
        return False

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
        
        # After adding columns, populate metadata from CSV
        logger.info("📄 Populating metadata from CSV...")
        populate_metadata_from_csv(engine)
        
        logger.info("🎉 Database schema fix completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
