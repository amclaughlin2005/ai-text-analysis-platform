"""
Analysis tasks for NLTK processing and LLM integration
Background jobs for sentiment analysis, topic modeling, entity extraction
"""

import sys
import os
from pathlib import Path
from celery import current_task
from typing import List, Dict, Any
from datetime import datetime

# Add the backend app to the path for imports
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from celery_config import celery_app
from app.core.logging import get_logger
from app.core.database import get_db_async, DatabaseTransaction
from app.analysis.nltk_processor import get_nltk_processor
from app.analysis.llm_processor import get_llm_processor
from app.models.dataset import Dataset, DatasetStatus
from app.models.question import Question
from app.models.analysis_job import AnalysisJob, JobStatus

logger = get_logger(__name__)

@celery_app.task(bind=True)
def process_dataset_with_nltk(self, dataset_id: str, user_id: str):
    """
    Process dataset with comprehensive NLTK analysis pipeline
    
    Args:
        dataset_id: ID of the dataset to process
        user_id: ID of the user who initiated the processing
    """
    logger.info(f"Starting NLTK processing for dataset {dataset_id}")
    
    try:
        # Update job status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing NLTK processor...'}
        )
        
        # Get processors
        nltk_processor = get_nltk_processor()
        llm_processor = get_llm_processor()
        
        # Get database session
        db = get_db_async()
        
        with DatabaseTransaction(db) as transaction:
            # Get dataset
            dataset = transaction.query(Dataset).filter_by(id=dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Update dataset status
            dataset.update_status(DatasetStatus.PROCESSING, "Starting NLTK analysis...")
            transaction.commit()
            
            # Get questions to process
            questions = transaction.query(Question).filter_by(
                dataset_id=dataset_id,
                is_valid=True
            ).all()
            
            if not questions:
                raise ValueError("No valid questions found in dataset")
            
            logger.info(f"Processing {len(questions)} questions")
            
            # Process questions in batches
            batch_size = 50
            total_questions = len(questions)
            processed_count = 0
            
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                
                # Update progress
                progress = (processed_count / total_questions) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed_count, 
                        'total': total_questions,
                        'status': f'Processing batch {i//batch_size + 1}...'
                    }
                )
                
                # Process batch
                batch_texts = [q.original_question for q in batch]
                
                # NLTK analysis
                batch_results = nltk_processor.analyze_batch(batch_texts)
                
                # Update questions with results
                for j, question in enumerate(batch):
                    if j < len(batch_results.get('sentiment_analysis', [])):
                        sentiment = batch_results['sentiment_analysis'][j]
                        question.update_sentiment_analysis(sentiment)
                    
                    if j < len(batch_results.get('classification_analysis', [])):
                        classification = batch_results['classification_analysis'][j]
                        question.update_classification(classification)
                    
                    if j < len(batch_results.get('readability_analysis', [])):
                        readability = batch_results['readability_analysis'][j]
                        question.update_readability(readability)
                    
                    question.mark_as_processed()
                
                processed_count += len(batch)
                transaction.commit()
                
                logger.info(f"Processed {processed_count}/{total_questions} questions")
            
            # Final dataset analysis summary
            summary_results = nltk_processor.get_analysis_summary({
                'sentiment_analysis': [q.sentiment_score for q in questions if q.sentiment_score],
                'entity_analysis': [],  # Would be populated from detailed analysis
                'processing_time': (datetime.now() - dataset.processing_started_at).total_seconds() if dataset.processing_started_at else 0
            })
            
            # Update dataset with summary
            dataset.update_analysis_summary(summary_results)
            dataset.update_status(DatasetStatus.COMPLETED, "NLTK analysis completed successfully")
            transaction.commit()
            
            logger.info(f"✅ Dataset {dataset_id} processing completed")
            
            return {
                'status': 'completed',
                'dataset_id': dataset_id,
                'processed_questions': processed_count,
                'summary': summary_results
            }
            
    except Exception as e:
        logger.error(f"❌ Dataset processing failed: {e}")
        
        # Update dataset status to failed
        try:
            with DatabaseTransaction() as transaction:
                dataset = transaction.query(Dataset).filter_by(id=dataset_id).first()
                if dataset:
                    dataset.update_status(DatasetStatus.FAILED, str(e))
                    transaction.commit()
        except:
            pass
        
        # Update task status
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'dataset_id': dataset_id}
        )
        
        raise e

@celery_app.task(bind=True)
def analyze_sentiment_batch(self, question_ids: List[str], user_id: str):
    """
    Batch sentiment analysis for specific questions
    
    Args:
        question_ids: List of question IDs to analyze
        user_id: ID of user who initiated the analysis
    """
    logger.info(f"Analyzing sentiment for {len(question_ids)} questions")
    
    try:
        nltk_processor = get_nltk_processor()
        db = get_db_async()
        
        with DatabaseTransaction(db) as transaction:
            questions = transaction.query(Question).filter(
                Question.id.in_(question_ids)
            ).all()
            
            processed = 0
            for question in questions:
                # Update progress
                progress = (processed / len(questions)) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={'current': processed, 'total': len(questions)}
                )
                
                # Analyze sentiment
                sentiment_result = nltk_processor.sentiment_analysis(question.original_question)
                question.update_sentiment_analysis(sentiment_result)
                
                processed += 1
            
            transaction.commit()
            
            return {
                'status': 'completed',
                'processed_questions': processed,
                'question_ids': question_ids
            }
            
    except Exception as e:
        logger.error(f"Batch sentiment analysis failed: {e}")
        raise e

@celery_app.task(bind=True)
def extract_entities_batch(self, question_ids: List[str], user_id: str):
    """
    Batch entity extraction for specific questions
    """
    logger.info(f"Extracting entities for {len(question_ids)} questions")
    
    try:
        nltk_processor = get_nltk_processor()
        db = get_db_async()
        
        with DatabaseTransaction(db) as transaction:
            questions = transaction.query(Question).filter(
                Question.id.in_(question_ids)
            ).all()
            
            processed = 0
            all_entities = []
            
            for question in questions:
                # Update progress
                progress = (processed / len(questions)) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={'current': processed, 'total': len(questions)}
                )
                
                # Extract entities
                entities = nltk_processor.entity_extraction(question.original_question)
                all_entities.append(entities)
                
                processed += 1
            
            transaction.commit()
            
            return {
                'status': 'completed',
                'processed_questions': processed,
                'entities': all_entities
            }
            
    except Exception as e:
        logger.error(f"Batch entity extraction failed: {e}")
        raise e

@celery_app.task(bind=True)
def generate_daily_analytics(self):
    """Generate daily analytics reports"""
    logger.info("Generating daily analytics")
    
    try:
        # This would implement daily analytics generation
        # For now, return a simple status
        return {
            "status": "Daily analytics generation - implementation pending",
            "date": datetime.now().isoformat(),
            "note": "Requires database with processed questions"
        }
        
    except Exception as e:
        logger.error(f"Daily analytics generation failed: {e}")
        raise e

@celery_app.task(bind=True) 
def test_nltk_processing(self):
    """Test task to verify NLTK processor is working"""
    logger.info("Testing NLTK processor")
    
    try:
        processor = get_nltk_processor()
        
        # Test text
        test_text = "I am very happy with the excellent customer service provided by your team today!"
        
        # Test all major functions
        results = {
            'sentiment': processor.sentiment_analysis(test_text),
            'entities': processor.entity_extraction(test_text),
            'keywords': processor.keyword_extraction(test_text),
            'readability': processor.readability_analysis(test_text),
            'classification': processor.question_classification(test_text)
        }
        
        logger.info("✅ NLTK processor test completed successfully")
        return {
            'status': 'success',
            'test_results': results,
            'message': 'All NLTK functions working correctly'
        }
        
    except Exception as e:
        logger.error(f"❌ NLTK processor test failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'message': 'NLTK processor test failed'
        }
