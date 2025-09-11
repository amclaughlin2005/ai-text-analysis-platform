"""
Dataset service layer for robust data upload and storage
Consolidates the best patterns from existing implementations
"""

import os
import csv
import io
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from fastapi import HTTPException, UploadFile

from ..models.dataset import Dataset, DatasetStatus
from ..models.question import Question
from ..models.analytics import WordFrequency
from ..models.analysis_job import AnalysisJob, JobType, JobStatus, JobPriority
from ..core.database import DatabaseTransaction
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure upload directory
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

class DatasetService:
    """
    Unified dataset service with robust error handling and validation
    """
    
    # File validation constants
    MAX_FILE_SIZE = settings.MAX_FILE_SIZE  # From config
    ALLOWED_EXTENSIONS = {'.csv'}
    ALLOWED_MIME_TYPES = {'text/csv', 'application/vnd.ms-excel', 'text/plain'}
    SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    # Required CSV column patterns
    QUESTION_PATTERNS = [
        'question', 'original question', 'user question', 
        'query', 'user query', 'original_question'
    ]
    RESPONSE_PATTERNS = [
        'response', 'human loop response', 'ai response', 
        'agent response', 'answer', 'reply', 'human_loop_response'
    ]

    @classmethod
    async def upload_dataset(
        cls,
        file: UploadFile,
        name: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Upload and process CSV dataset with comprehensive validation
        
        Args:
            file: Uploaded CSV file
            name: Dataset display name
            description: Optional dataset description
            user_id: User ID (for auth, optional for now)
            db: Database session
            
        Returns:
            Dictionary with upload result and dataset info
        """
        try:
            # Input validation
            cls._validate_upload_inputs(file, name)
            
            # File validation and processing
            file_content, encoding_used = await cls._process_uploaded_file(file)
            headers, rows = cls._parse_csv_content(file_content)
            cls._validate_csv_structure(headers, rows)
            
            # Generate unique identifiers
            dataset_id = uuid.uuid4()
            safe_filename = cls._generate_safe_filename(dataset_id, file.filename)
            file_path = UPLOAD_DIR / safe_filename
            
            # Use database transaction for atomicity
            with DatabaseTransaction(db) as transaction_db:
                # Save file to disk
                await cls._save_file_to_disk(file, file_path)
                
                try:
                    # Create dataset record
                    dataset = cls._create_dataset_record(
                        dataset_id=dataset_id,
                        name=name,
                        description=description,
                        file_info={
                            'original_filename': file.filename,
                            'file_path': str(file_path),
                            'file_size': file_path.stat().st_size,
                            'encoding': encoding_used
                        },
                        csv_info={
                            'headers': headers,
                            'total_rows': len(rows),
                            'total_columns': len(headers)
                        },
                        # user_id=user_id,  # Temporarily disabled for Railway compatibility
                        db=transaction_db
                    )
                    
                    # Create analysis job for background processing
                    analysis_job = cls._create_analysis_job(
                        dataset_id=dataset.id,
                        db=transaction_db
                    )
                    
                    # Process CSV rows into Question records
                    questions_created = cls._create_questions_from_csv(
                        dataset_id=dataset.id,
                        headers=headers,
                        rows=rows,
                        db=transaction_db
                    )
                    
                    # Update dataset with processing results
                    dataset.total_questions = questions_created
                    dataset.status = DatasetStatus.COMPLETED
                    dataset.processing_completed_at = datetime.utcnow()
                    
                    # Update job status
                    analysis_job.status = JobStatus.COMPLETED
                    analysis_job.end_time = datetime.utcnow()
                    
                    transaction_db.commit()
                    
                    logger.info(f"✅ Dataset uploaded successfully: {dataset.id} - {name}")
                    
                    return {
                        "success": True,
                        "message": f"Dataset '{name}' uploaded and processed successfully",
                        "dataset": dataset.to_dict(),
                        "processing": {
                            "questions_created": questions_created,
                            "job_id": str(analysis_job.id),
                            "status": "completed"
                        }
                    }
                    
                except Exception as e:
                    # Clean up file on database error
                    cls._cleanup_file(file_path)
                    raise
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Dataset upload failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {str(e)}"
            )

    @classmethod
    def get_datasets(
        cls,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get datasets with pagination and filtering
        """
        try:
            query = db.query(Dataset)
            
            # Filter by user if provided (for when auth is enabled)
            if user_id:
                pass  # query = query.filter(Dataset.user_id == user_id)  # Temporarily disabled for Railway
            
            # Get total count for pagination
            total_count = query.count()
            
            # Apply pagination and ordering
            datasets = query.order_by(desc(Dataset.created_at))\
                          .limit(limit)\
                          .offset(offset)\
                          .all()
            
            return {
                "datasets": [dataset.to_dict() for dataset in datasets],
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve datasets: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve datasets: {str(e)}"
            )

    @classmethod
    def get_dataset(cls, dataset_id: str, db: Session) -> Dict[str, Any]:
        """
        Get single dataset with detailed information
        """
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            # Get additional statistics
            questions_count = db.query(Question)\
                               .filter(Question.dataset_id == dataset_id)\
                               .count()
            
            word_frequencies_count = db.query(WordFrequency)\
                                      .filter(WordFrequency.dataset_id == dataset_id)\
                                      .count()
            
            dataset_dict = dataset.to_dict()
            dataset_dict['statistics'] = {
                'questions_count': questions_count,
                'word_frequencies_count': word_frequencies_count
            }
            
            return dataset_dict
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get dataset {dataset_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get dataset: {str(e)}"
            )

    @classmethod
    def delete_dataset(cls, dataset_id: str, db: Session) -> Dict[str, Any]:
        """
        Delete dataset and all associated data
        """
        try:
            with DatabaseTransaction(db) as transaction_db:
                dataset = transaction_db.query(Dataset)\
                                       .filter(Dataset.id == dataset_id)\
                                       .first()
                
                if not dataset:
                    raise HTTPException(status_code=404, detail="Dataset not found")
                
                # Clean up file
                if dataset.file_path and os.path.exists(dataset.file_path):
                    cls._cleanup_file(Path(dataset.file_path))
                
                # Delete dataset (cascades to related data)
                transaction_db.delete(dataset)
                transaction_db.commit()
                
                logger.info(f"✅ Dataset deleted: {dataset_id}")
                
                return {
                    "success": True,
                    "message": f"Dataset '{dataset.name}' deleted successfully"
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to delete dataset {dataset_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete dataset: {str(e)}"
            )

    # Private helper methods
    
    @classmethod
    def _validate_upload_inputs(cls, file: UploadFile, name: str):
        """Validate upload inputs"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File must be a CSV file. Got: {file_ext}"
            )
        
        # Check dataset name
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Dataset name is required")
        
        if len(name.strip()) > 255:
            raise HTTPException(status_code=400, detail="Dataset name too long (max 255 characters)")

    @classmethod
    async def _process_uploaded_file(cls, file: UploadFile) -> Tuple[str, str]:
        """Process uploaded file and detect encoding"""
        content = await file.read()
        
        # Check file size
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {cls.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Try multiple encodings
        for encoding in cls.SUPPORTED_ENCODINGS:
            try:
                text_content = content.decode(encoding)
                logger.info(f"✅ File decoded with encoding: {encoding}")
                return text_content, encoding
            except UnicodeDecodeError:
                continue
        
        raise HTTPException(
            status_code=400,
            detail="Could not decode CSV file. Please ensure it's saved with UTF-8, Latin-1, or Windows-1252 encoding."
        )

    @classmethod
    def _parse_csv_content(cls, content: str) -> Tuple[List[str], List[List[str]]]:
        """Parse CSV content into headers and rows"""
        try:
            csv_reader = csv.reader(io.StringIO(content))
            headers = next(csv_reader, [])
            rows = list(csv_reader)
            
            if not headers:
                raise HTTPException(status_code=400, detail="CSV file appears to be empty")
            
            logger.info(f"📊 CSV parsed: {len(headers)} columns, {len(rows)} rows")
            return headers, rows
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse CSV file: {str(e)}"
            )

    @classmethod
    def _validate_csv_structure(cls, headers: List[str], rows: List[List[str]]):
        """Validate CSV structure and required columns"""
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file contains no data rows")
        
        # Find required columns with flexible matching
        header_lower = [h.lower().strip() for h in headers]
        
        question_col = None
        response_col = None
        
        # Find question column
        for pattern in cls.QUESTION_PATTERNS:
            if pattern in header_lower:
                question_col = header_lower.index(pattern)
                break
        
        # Find response column
        for pattern in cls.RESPONSE_PATTERNS:
            if pattern in header_lower:
                response_col = header_lower.index(pattern)
                break
        
        missing_columns = []
        if question_col is None:
            missing_columns.append('question (or similar: original question, query)')
        if response_col is None:
            missing_columns.append('response (or similar: human loop response, answer)')
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}. "
                      f"Found columns: {', '.join(headers)}"
            )
        
        logger.info(f"✅ CSV validation passed - Question col: {question_col}, Response col: {response_col}")

    @classmethod
    def _generate_safe_filename(cls, dataset_id: uuid.UUID, original_filename: str) -> str:
        """Generate safe filename for storage"""
        # Sanitize original filename
        safe_original = "".join(c for c in original_filename if c.isalnum() or c in "._-")
        return f"{dataset_id}_{safe_original}"

    @classmethod
    async def _save_file_to_disk(cls, file: UploadFile, file_path: Path):
        """Save uploaded file to disk"""
        try:
            # Reset file pointer
            await file.seek(0)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            logger.info(f"✅ File saved: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

    @classmethod
    def _create_dataset_record(
        cls,
        dataset_id: uuid.UUID,
        name: str,
        description: Optional[str],
        file_info: Dict[str, Any],
        csv_info: Dict[str, Any],
        # user_id: Optional[str],  # Temporarily disabled for Railway compatibility
        db: Session
    ) -> Dataset:
        """Create dataset database record"""
        dataset = Dataset(
            id=dataset_id,
            # user_id=user_id,  # Temporarily disabled for Railway compatibility
            name=name.strip(),
            # description=description.strip() if description else None,  # Temporarily disabled - column doesn't exist on Railway
            file_path=file_info['file_path'],
            original_filename=file_info['original_filename'],
            file_size=file_info['file_size'],
            status=DatasetStatus.PROCESSING,
            csv_headers=csv_info['headers'],
            csv_encoding=file_info['encoding'],
            has_header_row=True,
            total_questions=csv_info['total_rows'],
            processing_started_at=datetime.utcnow()
        )
        
        db.add(dataset)
        db.flush()  # Get the ID without committing
        
        return dataset

    @classmethod
    def _create_analysis_job(cls, dataset_id: uuid.UUID, db: Session) -> AnalysisJob:
        """Create analysis job for background processing tracking"""
        job = AnalysisJob(
            dataset_id=dataset_id,
            user_id=None,  # Will be set when auth is enabled
            job_type=JobType.DATASET_PROCESSING,
            status=JobStatus.RUNNING,
            priority=JobPriority.NORMAL,
            start_time=datetime.utcnow()
        )
        
        db.add(job)
        db.flush()
        
        return job

    @classmethod
    def _create_questions_from_csv(
        cls,
        dataset_id: uuid.UUID,
        headers: List[str],
        rows: List[List[str]],
        db: Session
    ) -> int:
        """Create Question records from CSV data"""
        # Find column indices
        header_lower = [h.lower().strip() for h in headers]
        
        question_col = None
        response_col = None
        
        for pattern in cls.QUESTION_PATTERNS:
            if pattern in header_lower:
                question_col = header_lower.index(pattern)
                break
        
        for pattern in cls.RESPONSE_PATTERNS:
            if pattern in header_lower:
                response_col = header_lower.index(pattern)
                break
        
        questions_created = 0
        
        for row_num, row in enumerate(rows, start=1):
            # Skip empty rows or rows without question
            if (len(row) <= question_col or 
                not row[question_col] or 
                not row[question_col].strip()):
                continue
            
            question_text = row[question_col].strip()
            response_text = (row[response_col].strip() 
                           if response_col and len(row) > response_col and row[response_col]
                           else None)
            
            question = Question(
                dataset_id=dataset_id,
                csv_row_number=row_num,
                original_question=question_text,
                ai_response=response_text,
                question_length=len(question_text),
                response_length=len(response_text) if response_text else None,
                word_count_question=len(question_text.split()),
                word_count_response=len(response_text.split()) if response_text else None,
                is_valid=True  # Basic validation - can be enhanced
            )
            
            db.add(question)
            questions_created += 1
        
        logger.info(f"✅ Created {questions_created} questions for dataset {dataset_id}")
        return questions_created

    @classmethod
    def _cleanup_file(cls, file_path: Path):
        """Clean up uploaded file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"🗑️ Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup file {file_path}: {e}")
