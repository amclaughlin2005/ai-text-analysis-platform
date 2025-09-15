"""
Railway-compatible question creation service
Handles question import using pure SQL to avoid SQLAlchemy model schema mismatches
"""

import logging
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class RailwayQuestionService:
    """Service for creating questions compatible with Railway's database schema"""
    
    @staticmethod
    def create_questions_from_csv(
        dataset_id: uuid.UUID,
        headers: List[str],
        rows: List[List[str]],
        db: Session
    ) -> int:
        """
        Create questions from CSV data using pure SQL for Railway compatibility
        Only includes fields that are guaranteed to exist in Railway's questions table
        """
        try:
            # Use the same pattern matching logic as DatasetService for consistency
            header_lower = [h.lower().strip() for h in headers]
            
            # Import patterns from DatasetService to ensure consistency
            from ..services.dataset_service import DatasetService
            question_patterns = DatasetService.QUESTION_PATTERNS
            response_patterns = DatasetService.RESPONSE_PATTERNS
            
            logger.info(f"🔍 Regular session: Looking for question patterns {question_patterns} in headers: {header_lower}")
            logger.info(f"🔍 Original headers: {headers}")
            
            question_col = None
            response_col = None
            
            # Use exact matching like DatasetService validation
            for pattern in question_patterns:
                if pattern in header_lower:
                    question_col = header_lower.index(pattern)
                    logger.info(f"✅ Found question pattern '{pattern}' at index {question_col}")
                    break
            
            # Find response column  
            logger.info(f"🔍 Regular session: Looking for response patterns {response_patterns} in headers: {header_lower}")
            for pattern in response_patterns:
                if pattern in header_lower:
                    response_col = header_lower.index(pattern)
                    logger.info(f"✅ Found response pattern '{pattern}' at index {response_col}")
                    break
            
            if question_col is None or response_col is None:
                logger.error(f"❌ Regular session: Could not find question/response columns. Question col: {question_col}, Response col: {response_col}")
                logger.error(f"❌ Headers: {headers}")
                logger.error(f"❌ Lower headers: {header_lower}")
                logger.error(f"❌ Patterns: Q={question_patterns}, R={response_patterns}")
                
                # Try fallback with partial matching as a last resort
                logger.info("🔄 Trying fallback pattern matching...")
                for i, header in enumerate(header_lower):
                    if any(word in header for word in ['question', 'query', 'prompt']):
                        question_col = i
                        logger.info(f"✅ Fallback: Found question-like header '{header}' at index {i}")
                        break
                
                for i, header in enumerate(header_lower):
                    if any(word in header for word in ['response', 'answer', 'reply']):
                        response_col = i
                        logger.info(f"✅ Fallback: Found response-like header '{header}' at index {i}")
                        break
                
                if question_col is None or response_col is None:
                    logger.error(f"❌ Even fallback failed. Question col: {question_col}, Response col: {response_col}")
                    return 0
            
            logger.info(f"📝 Found question column at index {question_col}, response at {response_col}")
            
            questions_created = 0
            
            # Create questions using pure SQL - only minimal fields
            logger.info(f"📊 Processing {len(rows)} rows for question creation")
            
            for row_num, row in enumerate(rows, start=1):
                # Skip empty rows or rows without question/response
                if len(row) <= max(question_col, response_col):
                    logger.debug(f"⏭️ Row {row_num}: Not enough columns ({len(row)} vs needed {max(question_col, response_col) + 1})")
                    continue
                    
                if not row[question_col] or not row[response_col]:
                    logger.debug(f"⏭️ Row {row_num}: Empty question or response")
                    continue
                
                question_text = str(row[question_col]).strip()
                response_text = str(row[response_col]).strip()
                
                if not question_text or not response_text:
                    logger.debug(f"⏭️ Row {row_num}: Question or response is whitespace only")
                    continue
                
                logger.debug(f"🔄 Row {row_num}: Processing Q='{question_text[:50]}...' R='{response_text[:50]}...'")
                
                # Create a questions table if it doesn't exist and insert the question
                try:
                    # First, try to create the questions table if it doesn't exist (matching word cloud API expectations)
                    create_table_sql = text("""
                        CREATE TABLE IF NOT EXISTS questions (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            dataset_id UUID,
                            original_question TEXT,
                            ai_response TEXT,
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
                    db.execute(create_table_sql)
                    
                    # Now insert the question (including csv_row_number to satisfy NOT NULL constraint)
                    sql = text("""
                        INSERT INTO questions (id, dataset_id, original_question, ai_response, csv_row_number)
                        VALUES (:id, :dataset_id, :original_question, :ai_response, :csv_row_number)
                    """)
                    db.execute(sql, {
                        'id': str(uuid.uuid4()),
                        'dataset_id': str(dataset_id),
                        'original_question': question_text[:2000],
                        'ai_response': response_text[:5000],
                        'csv_row_number': row_num
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Row {row_num}: Failed to create/insert question: {e}")
                    logger.error(f"❌ Question text: {question_text[:100]}")
                    logger.error(f"❌ Response text: {response_text[:100]}")
                    continue
                
                questions_created += 1
                logger.debug(f"✅ Row {row_num}: Successfully created question {questions_created}")
            
            db.commit()
            
            logger.info(f"✅ Created {questions_created} questions for dataset {dataset_id}")
            return questions_created
            
        except Exception as e:
            logger.error(f"❌ Failed to create questions: {e}")
            db.rollback()
            return 0
    
    @staticmethod
    def get_questions_for_dataset(
        dataset_id: uuid.UUID,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get questions for a dataset using pure SQL
        """
        try:
            sql = text("""
                SELECT id, dataset_id, question_text, answer_text
                FROM questions 
                WHERE dataset_id = :dataset_id
                ORDER BY created_at ASC
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.execute(sql, {
                'dataset_id': str(dataset_id),
                'limit': limit,
                'offset': offset
            }).fetchall()
            
            questions = []
            for row in result:
                questions.append({
                    'id': str(row.id),
                    'dataset_id': str(row.dataset_id),
                    'question_text': row.question_text,
                    'answer_text': row.answer_text
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"❌ Failed to get questions: {e}")
            return []
    
    @staticmethod
    def create_questions_with_autocommit(
        dataset_id: uuid.UUID,
        headers: List[str],
        rows: List[List[str]],
        connection
    ) -> int:
        """
        Create questions using autocommit connection for Railway persistence
        """
        try:
            # Use the same improved pattern matching logic as regular session
            header_lower = [h.lower().strip() for h in headers]
            
            # Import patterns from DatasetService to ensure consistency
            from ..services.dataset_service import DatasetService
            question_patterns = DatasetService.QUESTION_PATTERNS
            response_patterns = DatasetService.RESPONSE_PATTERNS
            
            logger.info(f"🔍 Autocommit: Looking for question patterns {question_patterns} in headers: {header_lower}")
            logger.info(f"🔍 Original headers: {headers}")
            
            question_col = None
            response_col = None
            
            # Use exact matching like DatasetService validation
            for pattern in question_patterns:
                if pattern in header_lower:
                    question_col = header_lower.index(pattern)
                    logger.info(f"✅ Autocommit: Found question pattern '{pattern}' at index {question_col}")
                    break
            
            # Find response column  
            logger.info(f"🔍 Autocommit: Looking for response patterns {response_patterns} in headers: {header_lower}")
            for pattern in response_patterns:
                if pattern in header_lower:
                    response_col = header_lower.index(pattern)
                    logger.info(f"✅ Autocommit: Found response pattern '{pattern}' at index {response_col}")
                    break
            
            if question_col is None or response_col is None:
                logger.error(f"❌ Autocommit: Could not find question/response columns. Question col: {question_col}, Response col: {response_col}")
                logger.error(f"❌ Headers: {headers}")
                logger.error(f"❌ Lower headers: {header_lower}")
                logger.error(f"❌ Patterns: Q={question_patterns}, R={response_patterns}")
                
                # Try fallback with partial matching as a last resort
                logger.info("🔄 Autocommit: Trying fallback pattern matching...")
                for i, header in enumerate(header_lower):
                    if any(word in header for word in ['question', 'query', 'prompt']):
                        question_col = i
                        logger.info(f"✅ Autocommit fallback: Found question-like header '{header}' at index {i}")
                        break
                
                for i, header in enumerate(header_lower):
                    if any(word in header for word in ['response', 'answer', 'reply']):
                        response_col = i
                        logger.info(f"✅ Autocommit fallback: Found response-like header '{header}' at index {i}")
                        break
                
                if question_col is None or response_col is None:
                    logger.error(f"❌ Autocommit: Even fallback failed. Question col: {question_col}, Response col: {response_col}")
                    return 0
            
            logger.info(f"📝 Found question column at index {question_col}, response at {response_col}")
            
            questions_created = 0
            
            # First, ensure questions table exists (matching word cloud API expectations)
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS questions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    dataset_id UUID,
                    original_question TEXT,
                    ai_response TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            connection.execute(create_table_sql)
            
            # Create questions using autocommit connection
            for row_num, row in enumerate(rows, start=1):
                # Skip empty rows or rows without question/response
                if (len(row) <= max(question_col, response_col) or 
                    not row[question_col] or 
                    not row[response_col]):
                    continue
                
                question_text = str(row[question_col]).strip()
                response_text = str(row[response_col]).strip()
                
                if not question_text or not response_text:
                    continue
                
                try:
                    # Insert question with autocommit (including csv_row_number to satisfy NOT NULL constraint)
                    sql = text("""
                        INSERT INTO questions (id, dataset_id, original_question, ai_response, csv_row_number)
                        VALUES (:id, :dataset_id, :original_question, :ai_response, :csv_row_number)
                    """)
                    connection.execute(sql, {
                        'id': str(uuid.uuid4()),
                        'dataset_id': str(dataset_id),
                        'original_question': question_text[:2000],
                        'ai_response': response_text[:5000],
                        'csv_row_number': row_num
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to create question with autocommit: {e}")
                    continue
                
                questions_created += 1
            
            logger.info(f"✅ Created {questions_created} questions with autocommit for dataset {dataset_id}")
            return questions_created
            
        except Exception as e:
            logger.error(f"❌ Failed to create questions with autocommit: {e}")
            return 0
