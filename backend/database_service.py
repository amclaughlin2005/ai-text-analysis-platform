"""
Database service layer for the AI Text Analysis Platform
"""

import csv
import io
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from sqlalchemy.exc import IntegrityError

from database import get_db, create_all_tables, check_database_connection
from models import Dataset, Question, WordFrequency, AnalysisJob, LLMAnalysisCache, ApplicationSettings, INITIAL_SETTINGS

logger = logging.getLogger(__name__)

class DatabaseInitService:
    """
    Main service class for database initialization
    """
    
    @staticmethod
    def initialize_database() -> bool:
        """
        Initialize database with tables and default settings
        """
        try:
            # Check connection
            if not check_database_connection():
                return False
            
            # Create all tables
            if not create_all_tables():
                return False
            
            # Insert initial settings
            db = next(get_db())
            try:
                for setting_data in INITIAL_SETTINGS:
                    # Check if setting already exists
                    existing = db.query(ApplicationSettings).filter(
                        ApplicationSettings.setting_key == setting_data['setting_key']
                    ).first()
                    
                    if not existing:
                        setting = ApplicationSettings(**setting_data)
                        db.add(setting)
                        logger.info(f"✅ Added setting: {setting_data['setting_key']}")
                
                db.commit()
                logger.info("✅ Database initialized successfully with default settings")
                return True
                
            except Exception as e:
                db.rollback()
                logger.error(f"❌ Failed to insert initial settings: {e}")
                return False
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False

class DatasetService:
    """
    Service for dataset management operations
    """
    
    @staticmethod
    def create_dataset(
        name: str, 
        filename: str, 
        file_size: int, 
        file_path: str,
        column_names: List[str],
        total_rows: int,
        encoding: str = 'utf-8'
    ) -> Optional[Dataset]:
        """
        Create a new dataset record
        """
        db = next(get_db())
        try:
            dataset = Dataset(
                name=name,
                filename=filename,
                file_size=file_size,
                file_path=file_path,
                column_names=column_names,
                total_rows=total_rows,
                total_columns=len(column_names),
                encoding=encoding,
                upload_status='uploaded',
                processing_status='pending'
            )
            
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            
            logger.info(f"✅ Dataset created: {dataset.id} - {name}")
            return dataset
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create dataset: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_dataset(dataset_id: str) -> Optional[Dataset]:
        """
        Retrieve a dataset by ID
        """
        db = next(get_db())
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            return dataset
        except Exception as e:
            logger.error(f"❌ Failed to get dataset {dataset_id}: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_datasets(limit: int = 50, offset: int = 0) -> List[Dataset]:
        """
        Get all datasets with pagination
        """
        db = next(get_db())
        try:
            datasets = db.query(Dataset)\
                        .order_by(desc(Dataset.created_at))\
                        .limit(limit)\
                        .offset(offset)\
                        .all()
            return datasets
        except Exception as e:
            logger.error(f"❌ Failed to get datasets: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def update_dataset_processing_status(
        dataset_id: str, 
        status: str, 
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update dataset processing status
        """
        db = next(get_db())
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                return False
            
            dataset.processing_status = status
            if error_message:
                dataset.error_message = error_message
            if status == 'completed':
                dataset.processed_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"✅ Dataset {dataset_id} status updated to: {status}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update dataset status: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_dataset(dataset_id: str) -> bool:
        """
        Delete a dataset and all related data
        """
        db = next(get_db())
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                return False
            
            # Delete file if it exists
            if os.path.exists(dataset.file_path):
                os.remove(dataset.file_path)
            
            # Delete from database (cascades to questions, word_frequencies, etc.)
            db.delete(dataset)
            db.commit()
            
            logger.info(f"✅ Dataset {dataset_id} deleted successfully")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to delete dataset: {e}")
            return False
        finally:
            db.close()

class QuestionService:
    """
    Service for question management operations
    """
    
    @staticmethod
    def create_questions_from_csv(dataset_id: str, csv_file_path: str) -> int:
        """
        Parse CSV file and create question records
        """
        db = next(get_db())
        try:
            with open(csv_file_path, 'rb') as f:
                content = f.read()
            
            # Try multiple encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            csv_text = None
            
            for encoding in encodings:
                try:
                    csv_text = content.decode(encoding)
                    logger.info(f"✅ CSV decoded with {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if not csv_text:
                raise ValueError("Could not decode CSV with any supported encoding")
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(csv_text))
            headers = next(csv_reader, [])
            rows = list(csv_reader)
            
            # Find question and response columns
            question_col = None
            response_col = None
            
            for i, header in enumerate(headers):
                header_lower = header.lower().strip()
                if any(term in header_lower for term in ['question', 'original_question']):
                    question_col = i
                elif any(term in header_lower for term in ['response', 'human_loop_response']):
                    response_col = i
            
            if question_col is None:
                raise ValueError("Could not find question column in CSV")
            
            # Create question records
            questions_created = 0
            for row_num, row in enumerate(rows, start=1):
                if len(row) <= question_col or not row[question_col].strip():
                    continue
                
                question = Question(
                    dataset_id=dataset_id,
                    csv_row_number=row_num,
                    original_question=row[question_col].strip(),
                    ai_response=row[response_col].strip() if response_col and len(row) > response_col else None,
                    timestamp_from_csv=row[0].strip() if len(row) > 0 and row[0] else None,
                    project_id_from_csv=row[3].strip() if len(row) > 3 and row[3] else None,
                    user_id_from_csv=row[4].strip() if len(row) > 4 and row[4] else None,
                    question_length=len(row[question_col].strip()),
                    response_length=len(row[response_col].strip()) if response_col and len(row) > response_col else None,
                    word_count_question=len(row[question_col].strip().split()),
                    word_count_response=len(row[response_col].strip().split()) if response_col and len(row) > response_col else None
                )
                
                db.add(question)
                questions_created += 1
            
            # Update dataset with question count
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if dataset:
                dataset.questions_count = questions_created
                dataset.processing_status = 'completed'
                dataset.processed_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"✅ Created {questions_created} questions for dataset {dataset_id}")
            return questions_created
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create questions from CSV: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def get_questions_paginated(
        dataset_id: str, 
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[Question], int]:
        """
        Get paginated questions for a dataset
        """
        db = next(get_db())
        try:
            offset = (page - 1) * per_page
            
            questions = db.query(Question)\
                         .filter(Question.dataset_id == dataset_id)\
                         .order_by(asc(Question.csv_row_number))\
                         .limit(per_page)\
                         .offset(offset)\
                         .all()
            
            total_count = db.query(Question)\
                           .filter(Question.dataset_id == dataset_id)\
                           .count()
            
            return questions, total_count
            
        except Exception as e:
            logger.error(f"❌ Failed to get paginated questions: {e}")
            return [], 0
        finally:
            db.close()

class WordFrequencyService:
    """
    Service for word frequency operations
    """
    
    @staticmethod
    def generate_word_frequencies(
        dataset_id: str, 
        analysis_mode: str = 'all',
        selected_columns: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate word frequencies from dataset questions
        """
        db = next(get_db())
        try:
            # Get all questions for the dataset
            questions = db.query(Question)\
                         .filter(Question.dataset_id == dataset_id)\
                         .all()
            
            if not questions:
                return []
            
            # Extract text based on selected columns
            all_text_parts = []
            for question in questions:
                if selected_columns is None or 1 in selected_columns:
                    if question.original_question:
                        all_text_parts.append(question.original_question.lower())
                
                if selected_columns is None or 2 in selected_columns:
                    if question.ai_response:
                        all_text_parts.append(question.ai_response.lower())
            
            if not all_text_parts:
                return []
            
            # Word extraction and frequency counting
            import re
            from collections import Counter
            
            all_text = ' '.join(all_text_parts)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
            
            # Filter out noise words - Enhanced with comprehensive list
            noise_words_from_db = DatabaseUtilityService.get_setting('noise_words', [])
            
            # Comprehensive noise words list including all problematic words observed
            enhanced_noise_words = [
                # Original user-specified exclusions
                'details', 'page', 'https', 'filevineapp', 'docviewer', 
                'view', 'source', 'embedding', 'docwebviewer', 'com', 'www', 
                'html', 'link', 'url', 'href', 'retrieved', 'matching', 'appeared',
                
                # Legal document technical terms that aren't meaningful for analysis
                'singletonschreiber', 'filevineapp', 'docwebviewer',
                
                # Common filler words that appeared in results
                'that', 'this', 'from', 'with', 'they', 'have', 'will', 
                'about', 'information', 'could', 'would', 'should', 'when', 
                'where', 'there', 'what', 'please', 'question', 'see',
            ]
            
            # Combine database settings with enhanced list
            noise_words = list(set(noise_words_from_db + enhanced_noise_words))
            
            common_stops = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'use', 'man', 'new', 'now', 'old', 'see', 'him', 'two', 'how', 'its', 'who', 'oil', 'sit', 'set', 'run', 'eat', 'far', 'sea', 'eye', 'ask', 'put', 'end', 'why', 'let', 'say', 'she', 'may', 'try', 'own', 'too', 'any', 'yet', 'way', 'use', 'yes', 'has', 'his', 'her', 'him'
            }
            
            filtered_words = [w for w in words if w.lower() not in noise_words and w.lower() not in common_stops]
            word_counts = Counter(filtered_words)
            
            # Create word frequency records with enhanced processing
            word_data = []
            max_freq = max(word_counts.values()) if word_counts else 1
            
            # Try to use NLTK processor for advanced sentiment analysis
            try:
                from app.analysis.nltk_processor import get_nltk_processor
                nltk_processor = get_nltk_processor()
                use_advanced_sentiment = True
            except ImportError:
                use_advanced_sentiment = False
            
            for word, frequency in word_counts.most_common(50):  # Top 50 words
                # Enhanced sentiment analysis
                if use_advanced_sentiment:
                    # Use NLTK processor for more accurate sentiment
                    sentiment_result = nltk_processor.sentiment_analysis(word)
                    sentiment_score = sentiment_result.get('compound_score', 0.0)
                    if sentiment_score >= 0.05:
                        sentiment = 'positive'
                    elif sentiment_score <= -0.05:
                        sentiment = 'negative'
                    else:
                        sentiment = 'neutral'
                else:
                    # Fallback simple sentiment analysis
                    sentiment = 'neutral'
                    if word.lower() in ['excellent', 'great', 'good', 'helpful', 'satisfied', 'perfect', 'amazing']:
                        sentiment = 'positive'
                    elif word.lower() in ['bad', 'terrible', 'awful', 'frustrated', 'angry', 'disappointed']:
                        sentiment = 'negative'
                
                word_freq = WordFrequency(
                    dataset_id=dataset_id,
                    word=word,
                    frequency=frequency,
                    normalized_frequency=frequency / max_freq,
                    analysis_mode=analysis_mode,
                    columns_analyzed=selected_columns or [1, 2],
                    sentiment=sentiment,
                    category='legal' if dataset_id == '06a8437a-27e8-412f-a530-6cb04f7b6dc9' else 'general'
                )
                
                db.add(word_freq)
                
                word_data.append({
                    'word': word,
                    'frequency': frequency,
                    'sentiment': sentiment,
                    'size': frequency / max_freq
                })
            
            db.commit()
            logger.info(f"✅ Generated {len(word_data)} word frequencies for dataset {dataset_id}")
            return word_data
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to generate word frequencies: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_word_frequencies(
        dataset_id: str, 
        analysis_mode: str = 'all',
        limit: int = 50
    ) -> List[WordFrequency]:
        """
        Get existing word frequencies for a dataset
        """
        db = next(get_db())
        try:
            word_freqs = db.query(WordFrequency)\
                          .filter(
                              and_(
                                  WordFrequency.dataset_id == dataset_id,
                                  WordFrequency.analysis_mode == analysis_mode
                              )
                          )\
                          .order_by(desc(WordFrequency.frequency))\
                          .limit(limit)\
                          .all()
            
            return word_freqs
            
        except Exception as e:
            logger.error(f"❌ Failed to get word frequencies: {e}")
            return []
        finally:
            db.close()

class AnalysisJobService:
    """
    Service for background job management
    """
    
    @staticmethod
    def create_job(
        dataset_id: str,
        job_type: str,
        priority: int = 1
    ) -> Optional[AnalysisJob]:
        """
        Create a new analysis job
        """
        db = next(get_db())
        try:
            job = AnalysisJob(
                dataset_id=dataset_id,
                job_type=job_type,
                priority=priority,
                status='pending'
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            logger.info(f"✅ Analysis job created: {job.id} - {job_type}")
            return job
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create analysis job: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_job_progress(
        job_id: str,
        status: str,
        progress_percentage: int,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update job progress and status
        """
        db = next(get_db())
        try:
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if not job:
                return False
            
            job.status = status
            job.progress_percentage = progress_percentage
            if current_step:
                job.current_step = current_step
            if error_message:
                job.error_message = error_message
            
            if status == 'running' and not job.start_time:
                job.start_time = datetime.utcnow()
            elif status in ['completed', 'failed']:
                job.end_time = datetime.utcnow()
                if job.start_time:
                    duration = (job.end_time - job.start_time).total_seconds()
                    job.processing_duration_seconds = duration
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update job progress: {e}")
            return False
        finally:
            db.close()

class DatabaseUtilityService:
    """
    General database utility functions
    """
    
    @staticmethod
    def get_setting(setting_key: str, default_value: Any = None) -> Any:
        """
        Get application setting value
        """
        db = next(get_db())
        try:
            setting = db.query(ApplicationSettings)\
                       .filter(ApplicationSettings.setting_key == setting_key)\
                       .first()
            
            if setting:
                return setting.setting_value
            return default_value
            
        except Exception as e:
            logger.error(f"❌ Failed to get setting {setting_key}: {e}")
            return default_value
        finally:
            db.close()
    
    @staticmethod
    def update_setting(setting_key: str, setting_value: Any) -> bool:
        """
        Update application setting
        """
        db = next(get_db())
        try:
            setting = db.query(ApplicationSettings)\
                       .filter(ApplicationSettings.setting_key == setting_key)\
                       .first()
            
            if setting:
                setting.setting_value = setting_value
                setting.updated_at = datetime.utcnow()
            else:
                setting = ApplicationSettings(
                    setting_key=setting_key,
                    setting_value=setting_value,
                    setting_type='json'
                )
                db.add(setting)
            
            db.commit()
            logger.info(f"✅ Setting {setting_key} updated")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update setting {setting_key}: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """
        Get database statistics for monitoring
        """
        db = next(get_db())
        try:
            stats = {
                'total_datasets': db.query(Dataset).count(),
                'total_questions': db.query(Question).count(),
                'total_word_frequencies': db.query(WordFrequency).count(),
                'active_jobs': db.query(AnalysisJob).filter(AnalysisJob.status.in_(['pending', 'running'])).count(),
                'completed_jobs': db.query(AnalysisJob).filter(AnalysisJob.status == 'completed').count(),
                'cache_entries': db.query(LLMAnalysisCache).count(),
                'database_size_mb': 'N/A'  # SQLite file size would need OS check
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {}
        finally:
            db.close()
