"""
Dataset management API endpoints
Handles CSV upload, dataset CRUD operations, and processing status
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..core.database import get_db
from ..core.logging import get_logger
from ..services.dataset_service import DatasetService
from ..services.analysis_service import AnalysisService

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
@router.get("")
async def list_datasets(
    limit: int = Query(default=50, le=100, description="Number of datasets to return"),
    offset: int = Query(default=0, ge=0, description="Number of datasets to skip"),
    db: Session = Depends(get_db)
):
    """List all datasets with pagination"""
    logger.info(f"📊 Listing datasets: limit={limit}, offset={offset}")
    
    return DatasetService.get_datasets(
        limit=limit,
        offset=offset,
        db=db
    )

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(..., description="CSV file containing query-response pairs"),
    name: str = Form(..., description="Display name for the dataset"),
    description: Optional[str] = Form(None, description="Optional dataset description"),
    db: Session = Depends(get_db)
):
    """Upload and process CSV dataset with comprehensive validation"""
    logger.info(f"📤 Dataset upload request: {file.filename}, name: {name}")
    
    result = await DatasetService.upload_dataset(
        file=file,
        name=name,
        description=description,
        user_id=None,  # Will be set when auth is enabled
        db=db
    )
    
    return result

@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get dataset details with analysis results"""
    logger.info(f"📋 Getting dataset details: {dataset_id}")
    
    return DatasetService.get_dataset(dataset_id, db)

@router.get("/{dataset_id}/columns")
async def get_dataset_columns(dataset_id: str, db: Session = Depends(get_db)):
    """Get dataset column information for filtering"""
    logger.info(f"📊 Getting column info for dataset: {dataset_id}")
    
    try:
        from sqlalchemy import text
        
        # Check if dataset exists
        dataset_sql = text("SELECT name FROM datasets WHERE id = :dataset_id")
        dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
        
        if not dataset_result:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Return standard column structure for Q&A datasets
        return {
            "success": True,
            "columns": [
                {
                    "index": 0,
                    "name": "Questions", 
                    "type": "text",
                    "description": "Original questions from the dataset",
                    "sample": "Sample question text..."
                },
                {
                    "index": 1,
                    "name": "Responses",
                    "type": "text", 
                    "description": "AI responses and answers",
                    "sample": "Sample response text..."
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get columns for dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dataset columns: {str(e)}"
        )

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete dataset and all associated data"""
    logger.info(f"🗑️ Deleting dataset: {dataset_id}")
    
    return DatasetService.delete_dataset(dataset_id, db)

@router.post("/{dataset_id}/reprocess")
async def reprocess_dataset(
    dataset_id: str,
    analysis_mode: str = Form(default="all", description="Analysis mode for word frequency generation"),
    selected_columns: Optional[List[int]] = Form(default=[1, 2], description="CSV columns to analyze"),
    force_regenerate: bool = Form(default=False, description="Force regeneration of existing data"),
    db: Session = Depends(get_db)
):
    """Trigger dataset reprocessing and word frequency generation"""
    logger.info(f"🔄 Reprocessing dataset: {dataset_id} with mode: {analysis_mode}")
    
    # Verify dataset exists
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Generate word frequencies
    word_frequencies = AnalysisService.generate_word_frequencies(
        dataset_id=dataset_id,
        analysis_mode=analysis_mode,
        selected_columns=selected_columns,
        db=db,
        force_regenerate=force_regenerate
    )
    
    return {
        "success": True,
        "message": f"Dataset '{dataset['name']}' reprocessed successfully",
        "analysis_mode": analysis_mode,
        "word_frequencies_generated": len(word_frequencies),
        "word_frequencies": word_frequencies[:20]  # Return first 20 for preview
    }

@router.get("/{dataset_id}/word-frequencies")
async def get_word_frequencies(
    dataset_id: str,
    analysis_mode: str = Query(default="all", description="Analysis mode filter"),
    limit: int = Query(default=50, le=100, description="Number of words to return"),
    db: Session = Depends(get_db)
):
    """Get word frequencies for dataset visualization"""
    logger.info(f"📊 Getting word frequencies: {dataset_id} - {analysis_mode}")
    
    word_frequencies = AnalysisService.generate_word_frequencies(
        dataset_id=dataset_id,
        analysis_mode=analysis_mode,
        db=db,
        force_regenerate=False  # Use cached if available
    )
    
    return {
        "dataset_id": dataset_id,
        "analysis_mode": analysis_mode,
        "word_count": len(word_frequencies),
        "words": word_frequencies[:limit]
    }

@router.get("/debug/schema")
async def debug_questions_schema(db: Session = Depends(get_db)):
    """Debug endpoint to inspect questions table schema"""
    try:
        # Get table structure from PostgreSQL information_schema
        schema_sql = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'questions'
            ORDER BY ordinal_position
        """)
        
        result = db.execute(schema_sql).fetchall()
        
        columns = []
        for row in result:
            columns.append({
                "column_name": row.column_name,
                "data_type": row.data_type,
                "is_nullable": row.is_nullable,
                "column_default": row.column_default
            })
        
        # Skip constraints for now - just get basic schema
        constraints = []
        
        return {
            "table_name": "questions",
            "columns": columns,
            "constraints": constraints,
            "total_columns": len(columns)
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get schema info"}

@router.get("/{dataset_id}/questions")
async def get_dataset_questions(
    dataset_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get questions for a dataset with pagination (table view)"""
    try:
        logger.info(f"Fetching questions for dataset {dataset_id}")
        
        # Use the same query as word cloud API since that works
        questions_sql = text("SELECT original_question, ai_response FROM questions WHERE dataset_id = :dataset_id ORDER BY csv_row_number ASC")
        questions_result = db.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
        
        # Calculate pagination
        total = len(questions_result)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_questions = questions_result[start_idx:end_idx]
        
        # Format for table view (match frontend interface)
        questions = []
        for i, row in enumerate(paginated_questions):
            questions.append({
                "id": str(start_idx + i + 1),
                "original_question": str(row[0]) if row[0] else "",
                "ai_response": str(row[1]) if row[1] else "",
                "created_at": None
            })
        
        return {
            "success": True,
            "data": questions,
            "total": total,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        logger.error(f"Questions API error for dataset {dataset_id}: {e}")
        return {
            "success": False,
            "data": [],
            "total": 0,
            "error": str(e),
            "pagination": {
                "page": 1,
                "per_page": per_page,
                "total_count": 0,
                "total_pages": 0
            }
        }

@router.post("/{dataset_id}/append")
async def append_data_to_dataset(
    dataset_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Append new data to an existing dataset"""
    try:
        from ..services.dataset_service import DatasetService
        from ..services.railway_question_service import RailwayQuestionService
        
        logger.info(f"📝 Appending data to dataset: {dataset_id}")
        logger.info(f"📁 File: {file.filename}, Size: {file.size} bytes")
        
        # Verify dataset exists
        existing_dataset = DatasetService.get_dataset(dataset_id, db)
        if not existing_dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Read and validate file
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        # Process the file and append questions
        try:
            # Use the Railway question service to append questions
            questions_created = await RailwayQuestionService.append_questions_to_dataset(
                dataset_id=dataset_id,
                file_content=file_content,
                filename=file.filename,
                db=db
            )
            
            # Update dataset statistics
            DatasetService.update_dataset_stats(dataset_id, db)
            
            logger.info(f"✅ Successfully appended {questions_created} questions to dataset {dataset_id}")
            
            return {
                "success": True,
                "message": f"Successfully appended {questions_created} questions to dataset",
                "dataset_id": dataset_id,
                "questions_added": questions_created,
                "filename": file.filename
            }
            
        except Exception as processing_error:
            logger.error(f"❌ Failed to process appended file: {processing_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file: {str(processing_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Append data operation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Append operation failed: {str(e)}"
        )

@router.post("/merge")
async def merge_datasets(
    source_dataset_ids: List[str] = Form(..., description="List of dataset IDs to merge"),
    target_name: str = Form(..., description="Name for the new merged dataset"),
    target_description: Optional[str] = Form(None, description="Optional description for merged dataset"),
    delete_source: bool = Form(False, description="Whether to delete source datasets after merge"),
    db: Session = Depends(get_db)
):
    """Merge multiple datasets into a new dataset"""
    try:
        import uuid
        from ..models.dataset import Dataset
        from ..models.question import Question
        
        logger.info(f"🔗 Starting merge operation: {len(source_dataset_ids)} datasets -> '{target_name}'")
        
        if len(source_dataset_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 datasets required for merge")
        
        # Verify all source datasets exist
        source_datasets = []
        total_questions = 0
        
        for dataset_id in source_dataset_ids:
            dataset_sql = text("SELECT id, name, filename FROM datasets WHERE id = :dataset_id")
            dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
            
            if not dataset_result:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
            
            # Count questions in this dataset
            count_sql = text("SELECT COUNT(*) FROM questions WHERE dataset_id = :dataset_id")
            question_count = db.execute(count_sql, {"dataset_id": dataset_id}).scalar()
            
            source_datasets.append({
                "id": dataset_result[0],
                "name": dataset_result[1], 
                "filename": dataset_result[2],
                "question_count": question_count
            })
            total_questions += question_count
            
        if total_questions == 0:
            raise HTTPException(status_code=400, detail="No questions found in source datasets")
        
        logger.info(f"📊 Source datasets validation complete: {total_questions} total questions")
        
        # Create new target dataset
        target_dataset_id = str(uuid.uuid4())
        
        create_dataset_sql = text("""
            INSERT INTO datasets (id, name, filename, file_size, file_path, original_filename, 
                                created_at, updated_at, upload_status, processing_status, status, 
                                total_questions, processed_questions, valid_questions, invalid_questions,
                                csv_delimiter, csv_encoding, has_header_row, organizations_count, is_public,
                                total_rows, total_columns, progress_percentage)
            VALUES (:id, :name, :filename, :file_size, :file_path, :original_filename,
                   NOW(), NOW(), 'completed', 'completed', 'completed',
                   :total_questions, :processed_questions, :valid_questions, :invalid_questions,
                   ',', 'utf-8', TRUE, 0, FALSE,
                   :total_rows, 2, 100.0)
        """)
        
        merged_filename = f"merged_{len(source_dataset_ids)}_datasets.json"
        merged_file_path = f"/merged/{target_dataset_id}/{merged_filename}"
        estimated_size = total_questions * 500  # Rough estimate
        
        db.execute(create_dataset_sql, {
            "id": target_dataset_id,
            "name": target_name,
            "filename": merged_filename,
            "file_size": estimated_size,
            "file_path": merged_file_path,
            "original_filename": merged_filename,
            "total_questions": total_questions,
            "processed_questions": total_questions,
            "valid_questions": total_questions,
            "invalid_questions": 0,
            "total_rows": total_questions  # Each question is a row
        })
        
        # Copy all questions from source datasets to target dataset
        questions_copied = 0
        
        for source_dataset in source_datasets:
            copy_questions_sql = text("""
                INSERT INTO questions (id, dataset_id, original_question, ai_response, org_name, user_id_from_csv, csv_row_number, is_valid, created_at, updated_at)
                SELECT 
                    UUID() as id,
                    :target_dataset_id as dataset_id,
                    original_question,
                    ai_response, 
                    org_name,
                    user_id_from_csv,
                    csv_row_number,
                    is_valid,
                    NOW() as created_at,
                    NOW() as updated_at
                FROM questions 
                WHERE dataset_id = :source_dataset_id
            """)
            
            result = db.execute(copy_questions_sql, {
                "target_dataset_id": target_dataset_id,
                "source_dataset_id": source_dataset["id"]
            })
            
            copied_count = result.rowcount if hasattr(result, 'rowcount') else source_dataset["question_count"]
            questions_copied += copied_count
            
            logger.info(f"✅ Copied {copied_count} questions from dataset '{source_dataset['name']}'")
        
        # Update target dataset with actual counts
        update_dataset_sql = text("""
            UPDATE datasets 
            SET file_size = :actual_size,
                total_questions = :actual_questions,
                processed_questions = :actual_questions,
                valid_questions = :actual_questions,
                total_rows = :actual_questions
            WHERE id = :dataset_id
        """)
        
        db.execute(update_dataset_sql, {
            "dataset_id": target_dataset_id,
            "actual_size": questions_copied * 150,  # More accurate estimate based on actual data
            "actual_questions": questions_copied
        })
        
        # Delete source datasets if requested
        deleted_datasets = []
        if delete_source:
            for source_dataset in source_datasets:
                try:
                    # Delete questions first
                    delete_questions_sql = text("DELETE FROM questions WHERE dataset_id = :dataset_id")
                    db.execute(delete_questions_sql, {"dataset_id": source_dataset["id"]})
                    
                    # Delete dataset
                    delete_dataset_sql = text("DELETE FROM datasets WHERE id = :dataset_id")
                    db.execute(delete_dataset_sql, {"dataset_id": source_dataset["id"]})
                    
                    deleted_datasets.append(source_dataset["name"])
                    logger.info(f"🗑️ Deleted source dataset '{source_dataset['name']}'")
                    
                except Exception as delete_error:
                    logger.warning(f"⚠️ Failed to delete dataset {source_dataset['id']}: {delete_error}")
        
        # Commit all changes
        db.commit()
        
        logger.info(f"🎉 Merge completed successfully: {questions_copied} questions in new dataset '{target_name}'")
        
        return {
            "success": True,
            "message": f"Successfully merged {len(source_dataset_ids)} datasets",
            "target_dataset_id": target_dataset_id,
            "target_dataset_name": target_name,
            "questions_merged": questions_copied,
            "source_datasets": [ds["name"] for ds in source_datasets],
            "deleted_datasets": deleted_datasets if delete_source else [],
            "total_source_datasets": len(source_dataset_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dataset merge failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Merge operation failed: {str(e)}"
        )
