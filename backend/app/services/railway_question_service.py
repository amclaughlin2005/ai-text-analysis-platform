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
            # Find column indices for question and response
            header_lower = [h.lower().strip() for h in headers]
            
            # Common patterns for question and response columns
            question_patterns = ['question', 'original_question', 'query', 'prompt', 'input']
            response_patterns = ['response', 'answer', 'ai_response', 'output', 'reply']
            
            question_col = None
            response_col = None
            
            # Find question column
            for pattern in question_patterns:
                for i, header in enumerate(header_lower):
                    if pattern in header:
                        question_col = i
                        break
                if question_col is not None:
                    break
            
            # Find response column  
            for pattern in response_patterns:
                for i, header in enumerate(header_lower):
                    if pattern in header:
                        response_col = i
                        break
                if response_col is not None:
                    break
            
            if question_col is None or response_col is None:
                logger.warning(f"Could not find question/response columns in headers: {headers}")
                return 0
            
            logger.info(f"📝 Found question column at index {question_col}, response at {response_col}")
            
            questions_created = 0
            
            # Create questions using pure SQL - only minimal fields
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
                
                # Create a questions table if it doesn't exist and insert the question
                try:
                    # First, try to create the questions table if it doesn't exist
                    create_table_sql = text("""
                        CREATE TABLE IF NOT EXISTS questions (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            dataset_id UUID,
                            question_text TEXT,
                            answer_text TEXT,
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
                    db.execute(create_table_sql)
                    
                    # Now insert the question
                    sql = text("""
                        INSERT INTO questions (id, dataset_id, question_text, answer_text)
                        VALUES (:id, :dataset_id, :question_text, :answer_text)
                    """)
                    db.execute(sql, {
                        'id': str(uuid.uuid4()),
                        'dataset_id': str(dataset_id),
                        'question_text': question_text[:2000],
                        'answer_text': response_text[:5000]
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to create/insert question: {e}")
                    # If all else fails, just skip this question but log it
                    continue
                
                questions_created += 1
            
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
